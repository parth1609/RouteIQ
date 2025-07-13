import torch
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import (
    GPT2LMHeadModel, 
    GPT2Tokenizer, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from torch.utils.data import DataLoader
import numpy as np
import os
import json
import ast
import re

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

class ITTicketClassifierProcessor:
    def __init__(self, model_name="gpt2"):
        self.model_name = model_name
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.special_tokens = {
            "query_start": "<QUERY>",
            "classify_start": "<CLASSIFY>",
            "json_start": "<JSON>",
            "json_end": "</JSON>",
            "end_token": "<END>"
        }
        self.tokenizer.add_special_tokens({
            "additional_special_tokens": list(self.special_tokens.values())
        })


    def load_dataset(self, dataset_name="parth1609/IT_ticket_dataset"):
        from datasets import load_dataset
        print(f"Loading dataset: {dataset_name}")
        return load_dataset(dataset_name)

    def clean_tags(self, tags_str):
        try:
            if pd.isna(tags_str):
                return []
            if isinstance(tags_str, str):
                tags_str = tags_str.strip()
                if tags_str.startswith('[') and tags_str.endswith(']'):
                    tags = ast.literal_eval(tags_str)
                    return tags if isinstance(tags, list) else [str(tags)]
                else:
                    return [tags_str]
            return tags_str if isinstance(tags_str, list) else [str(tags_str)]
        except:
            return []
        
    def format_training_example(self, row):
        body = str(row['Body']) if pd.notna(row['Body']) else ""
        department = str(row['Department']) if pd.notna(row['Department']) else ""
        priority = str(row['Priority']) if pd.notna(row['Priority']) else ""
        body = ' '.join(body.split())

        json_output = {"department": department, "priority": priority}
        formatted_text = (
            f"{self.special_tokens['query_start']} {body} "
            f"{self.special_tokens['classify_start']} "
            f"{self.special_tokens['json_start']} {json.dumps(json_output)} {self.special_tokens['json_end']} "
            f"{self.special_tokens['end_token']}"
        )
        return formatted_text

    def prepare_dataset(self, dataset, max_length=512):
        print("Preparing dataset...")
        df = dataset['train'].to_pandas()
        formatted_texts = []
        for idx, row in df.iterrows():
            if pd.isna(row['Body']) or pd.isna(row['Department']) or pd.isna(row['Priority']):
                continue
            formatted_texts.append(self.format_training_example(row))
        print(f"Created {len(formatted_texts)} training examples")

        # 1) Build a HuggingFace Dataset from our list of strings
        raw_ds = Dataset.from_dict({"text": formatted_texts})

        # 2) Tokenize, removing the raw "text" column so only input_ids/etc remain
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=max_length
            )

        tokenized = raw_ds.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"],
        )

        # 3) Split
        split = tokenized.train_test_split(test_size=0.1, seed=42)
        return DatasetDict(train=split["train"], validation=split["test"])

class GPT2ITClassifier:
    def __init__(self, model_name="gpt2", processor=None):
        """Initialize the classifier"""
        self.model_name = model_name
        self.processor = processor
        
        # Load model and resize embeddings for new tokens
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.resize_token_embeddings(len(self.processor.tokenizer))
        
    def setup_training_args(self, output_dir="./gpt2-it-classifier", **kwargs):
        """Setup training arguments"""
        default_args = {
            "output_dir": output_dir,
            "overwrite_output_dir": True,
            "num_train_epochs": 3,
            "per_device_train_batch_size": 4,
            "per_device_eval_batch_size": 4,
            "gradient_accumulation_steps": 2,
            "warmup_steps": 100,
            "logging_steps": 50,
            "save_steps": 500,
            "eval_steps": 500,
            "eval_strategy": "steps",
            "save_strategy": "steps",
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "learning_rate": 5e-5,
            "weight_decay": 0.01,
            "lr_scheduler_type": "cosine",
            "seed": 42,
            "fp16": torch.cuda.is_available(),
            "dataloader_pin_memory": False,
            "remove_unused_columns": False,
        }
        
        # Update with any user-provided arguments
        default_args.update(kwargs)
        
        return TrainingArguments(**default_args)
    
    def train(self, tokenized_dataset, training_args):
        """Train the model"""
        print("Setting up trainer...")
        
        # Data collator for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.processor.tokenizer,
            mlm=False,  # GPT-2 is autoregressive, not masked LM
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset['train'],
            eval_dataset=tokenized_dataset['validation'],
            data_collator=data_collator,
            tokenizer=self.processor.tokenizer,
        )
        
        print("Starting training...")
        # Train the model
        trainer.train()
        
        # Save the final model
        print("Saving model...")
        trainer.save_model()
        self.processor.tokenizer.save_pretrained(training_args.output_dir)
        
        return trainer
    
    def classify_query(self, customer_query, max_length=200, temperature=0.3):
        """Classify a customer query and return JSON format"""
        self.model.eval()
        
        # Format the input prompt
        prompt = f"{self.processor.special_tokens['query_start']} {customer_query} {self.processor.special_tokens['classify_start']} {self.processor.special_tokens['json_start']}"
        
        # Encode the prompt
        input_ids = self.processor.tokenizer.encode(prompt, return_tensors='pt').to(device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_length=len(input_ids[0]) + 100,  # Generate reasonable length
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.processor.tokenizer.eos_token_id,
                eos_token_id=self.processor.tokenizer.encode(self.processor.special_tokens['json_end'])[0],
                num_return_sequences=1
            )
        
        # Decode the generated text
        generated_text = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Extract JSON from the generated text
        return self.extract_classification_json(generated_text, customer_query)
    
    def extract_classification_json(self, generated_text, original_query):
        """Extract and parse the JSON classification from generated text"""
        try:
            # Find the JSON content between <JSON> and </JSON>
            json_start = generated_text.find(self.processor.special_tokens['json_start'])
            json_end = generated_text.find(self.processor.special_tokens['json_end'])
            
            if json_start != -1 and json_end != -1:
                json_start += len(self.processor.special_tokens['json_start'])
                json_content = generated_text[json_start:json_end].strip()
                
                # Try to parse the JSON
                try:
                    classification = json.loads(json_content)
                    # Add the original query to the result
                    result = {
                        "query": original_query,
                        "department": classification.get("department", "Unknown"),
                        "priority": classification.get("priority", "Unknown")
                    }
                    return result
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract department and priority manually
                    return self.fallback_extraction(json_content, original_query)
            else:
                # Fallback if no JSON tags found
                return self.fallback_extraction(generated_text, original_query)
                
        except Exception as e:
            print(f"Error extracting JSON: {e}")
            return {
                "query": original_query,
                "department": "Unknown",
                "priority": "Unknown",
                "error": str(e)
            }
    
    def fallback_extraction(self, text, original_query):
        """Fallback method to extract department and priority from text"""
        # Simple regex patterns to find department and priority
        dept_pattern = r'"department":\s*"([^"]*)"'
        priority_pattern = r'"priority":\s*"([^"]*)"'
        
        dept_match = re.search(dept_pattern, text, re.IGNORECASE)
        priority_match = re.search(priority_pattern, text, re.IGNORECASE)
        
        department = dept_match.group(1) if dept_match else "Unknown"
        priority = priority_match.group(1) if priority_match else "Unknown"
        
        return {
            "query": original_query,
            "department": department,
            "priority": priority
        }

def main():
    """Main training function"""
    print("=== GPT-2 IT Ticket Classifier Training ===")
    
    # Initialize processor
    processor = ITTicketClassifierProcessor(model_name="gpt2")
    
    # Load and prepare dataset
    dataset = processor.load_dataset()
    tokenized_dataset = processor.prepare_dataset(dataset, max_length=512)
    
    print(f"Training samples: {len(tokenized_dataset['train'])}")
    print(f"Validation samples: {len(tokenized_dataset['validation'])}")
    
    # Initialize classifier
    classifier = GPT2ITClassifier(model_name="gpt2", processor=processor)
    
    # Setup training arguments
    training_args = classifier.setup_training_args(
        output_dir="./gpt2-it-classifier",
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Reduce if running out of memory
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=5e-5,
        warmup_steps=100,
        logging_steps=50,
        save_steps=1000,
        eval_steps=1000,
    )
    
    # Train the model
    trained_trainer = classifier.train(tokenized_dataset, training_args)
    
    print("Training completed!")
    
    # Test classification
    print("\n=== Testing Classification ===")
    test_queries = [
        "I can't access my email account",
        "The server is down and no one can connect",
        "My computer won't start this morning",
        "We need a new software license for the team",
        "The network is running very slowly",
        "I forgot my password and need to reset it"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = classifier.classify_query(query, temperature=0.3)
        print(f"Classification: {json.dumps(result, indent=2)}")
        print("-" * 80)

def load_trained_classifier(model_path="./gpt2-it-classifier"):
    """Load a previously trained classifier for inference"""
    print(f"Loading trained classifier from {model_path}")
    
    # Initialize processor with trained tokenizer
    processor = ITTicketClassifierProcessor()
    processor.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    
    # Initialize classifier with trained model
    classifier = GPT2ITClassifier(processor=processor)
    classifier.model = GPT2LMHeadModel.from_pretrained(model_path)
    classifier.model.to(device)
    
    return classifier, processor

def interactive_classification():
    """Interactive ticket classification"""
    print("Loading trained classifier...")
    classifier, processor = load_trained_classifier()
    
    print("=== Interactive IT Ticket Classification ===")
    print("Enter customer queries to classify them. Type 'quit' to exit.")
    
    while True:
        user_input = input("\nEnter customer query (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        
        # Classify the query
        result = classifier.classify_query(user_input, temperature=0.3)
        print(f"\nClassification Result:")
        print(json.dumps(result, indent=2))
        print("-" * 80)

def batch_classify_queries(queries_file=None, queries_list=None):
    """Classify multiple queries and return results"""
    print("Loading trained classifier...")
    classifier, processor = load_trained_classifier()
    
    queries = []
    if queries_file:
        with open(queries_file, 'r') as f:
            queries = [line.strip() for line in f if line.strip()]
    elif queries_list:
        queries = queries_list
    else:
        print("No queries provided")
        return
    
    results = []
    print(f"Classifying {len(queries)} queries...")
    
    for i, query in enumerate(queries):
        print(f"Processing {i+1}/{len(queries)}: {query[:50]}...")
        result = classifier.classify_query(query, temperature=0.3)
        results.append(result)
    
    return results

if __name__ == "__main__":
    # Uncomment the function you want to run:
    
    # Train the classifier
    # main()
    
    # Or run interactive classification (after training)
    # interactive_classification()
    
    # Or classify a batch of queries
    sample_queries = [
        "Email not working, urgent issue",
        "Need new laptop for new employee", 
        "Server maintenance required",
        "Password reset needed"
    ]
    results = batch_classify_queries(queries_list=sample_queries)
    for result in results:
        print(json.dumps(result, indent=2))