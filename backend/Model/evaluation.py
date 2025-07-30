#!/usr/bin/env python3
"""
IT Ticket Classification Evaluation Module

This module provides functionality to evaluate IT ticket classification models
using both Hugging Face Inference API and local model inference.

Author: Generated from evaluation notebook

"""

import json
import os
import requests
import torch
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel

# Import custom classes (ensure gp2_finetune.py is in the same directory)
try:
    from Model.gp2_finetune import ITTicketClassifierProcessor, GPT2ITClassifier
except ImportError:
    print("Warning: Could not import custom classes from Model.gp2_finetune.py")
    ITTicketClassifierProcessor = None
    GPT2ITClassifier = None


class ITTicketEvaluator:
    """
    A comprehensive evaluator for IT ticket classification models.
    
    This class provides methods to evaluate models using different approaches:
    1. Hugging Face Inference API
    2. Local transformers pipeline
    3. Custom GPT2 classifier
    """
    
    def __init__(self, model_id: str = None, api_token: str = None):
        """
        Initialize the evaluator.
        
        Args:
            model_id (str): Hugging Face model ID
            api_token (str): Hugging Face API token
        """
        # Load environment variables
        load_dotenv()
        
        # Set model configuration
        self.model_id = model_id or os.getenv('HF_MODEL_ID') 
        self.api_token = api_token or os.getenv("HF_TOKEN")
        
        # Validate API token
        if not self.api_token:
            print("Warning: Hugging Face API token not found. API-based evaluation will not work.")
        
        # Set up API configuration
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Set up device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize components
        self.pipeline = None
        self.custom_classifier = None
        
    def setup_pipeline(self) -> None:
        """
        Initialize the transformers pipeline for text generation.
        """
        try:
            self.pipeline = pipeline(
                "text-generation",  # Changed from text2text-generation
                model=self.model_id,
                tokenizer=self.model_id,
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ Pipeline initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize pipeline: {e}")
            self.pipeline = None
    
    def setup_custom_classifier(self) -> None:
        """
        Initialize the custom GPT2 classifier.
        """
        if ITTicketClassifierProcessor is None or GPT2ITClassifier is None:
            print("❌ Custom classifier classes not available")
            return
            
        try:
            # Initialize processor and classifier
            processor = ITTicketClassifierProcessor(model_name=self.model_id)
            self.custom_classifier = GPT2ITClassifier(model_name=self.model_id, processor=processor)
            
            # Move to device and set to eval mode
            self.custom_classifier.model.to(self.device)
            self.custom_classifier.model.eval()
            print("✅ Custom classifier initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize custom classifier: {e}")
            self.custom_classifier = None
    
    def query_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a query to the Hugging Face Inference API.
        
        Args:
            payload (Dict): The payload to send to the API
            
        Returns:
            Dict: API response
        """
        if not self.api_token:
            raise ValueError("API token not available")
            
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return {"error": str(e)}
    
    def classify_with_pipeline(self, tickets: List[str]) -> List[Dict[str, Any]]:
        """
        Classify tickets using the transformers pipeline.
        
        Args:
            tickets (List[str]): List of ticket descriptions
            
        Returns:
            List[Dict]: Classification results
        """
        if self.pipeline is None:
            self.setup_pipeline()
            
        if self.pipeline is None:
            return [{"error": "Pipeline not available"}] * len(tickets)
        
        results = []
        print(f"\n=== Pipeline Classification ===\nClassifying {len(tickets)} tickets...")
        
        for i, ticket in enumerate(tickets):
            print(f"Processing {i+1}/{len(tickets)}: {ticket[:50]}...")
            
            prompt = (
                "Classify the following IT ticket and return output in JSON format with keys:\n"
                "'ticket', 'Department', 'Priority'.\n\n"
                f"Ticket: \"{ticket}\""
            )
            
            try:
                output = self.pipeline(
                    prompt,
                    max_new_tokens=128,
                    do_sample=False,
                    pad_token_id=self.pipeline.tokenizer.eos_token_id
                )
                text = output[0]["generated_text"].strip()
                
                result = {
                    "ticket": ticket,
                    "model_output": text,
                    "method": "pipeline"
                }
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error processing ticket: {e}")
                results.append({
                    "ticket": ticket,
                    "error": str(e),
                    "method": "pipeline"
                })
        
        return results
    
    def classify_with_custom_classifier(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Classify queries using the custom GPT2 classifier.
        
        Args:
            queries (List[str]): List of query descriptions
            
        Returns:
            List[Dict]: Classification results
        """
        if self.custom_classifier is None:
            self.setup_custom_classifier()
            
        if self.custom_classifier is None:
            return [{"error": "Custom classifier not available"}] * len(queries)
        
        results = []
        print(f"\n=== Custom Classifier Evaluation ===\nClassifying {len(queries)} queries...")
        
        for i, query in enumerate(queries):
            print(f"Processing {i+1}/{len(queries)}: {query[:50]}...")
            
            try:
                result = self.custom_classifier.classify_query(query, temperature=0.3)
                result["method"] = "custom_classifier"
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "method": "custom_classifier"
                })
        
        return results
    
    def print_results(self, results: List[Dict[str, Any]], title: str = "Results") -> None:
        """
        Print classification results in a formatted way.
        
        Args:
            results (List[Dict]): Results to print
            title (str): Title for the results section
        """
        print(f"\n--- {title} ---")
        for result in results:
            if "error" not in result:
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Error: {result}")
            print("-" * 60)
    
    def run_comprehensive_evaluation(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run a comprehensive evaluation using all available methods.
        
        Returns:
            Dict: Results from all evaluation methods
        """
        # Sample data for evaluation
        sample_tickets = [
            "My laptop is not turning on after the latest update.",
            "The VPN disconnects every time I upload files.",
            "Unable to access email - Authentication error prevents login to Outlook",
            "HP LaserJet printer offline and unresponsive to print commands",
            "Critical performance degradation on company intranet portal",
            "Print jobs stuck in queue and not processing on network printer",
            "Network printer showing offline status and connection errors",
        ]
        
        sample_queries = [
            "Email not working, urgent issue",
            "Need new laptop for new employee",
            "Urgent: Our main production server is down, impacting all critical services. Users are unable to access core applications, leading to significant business disruption. We require immediate assistance to diagnose and restore service to prevent further financial losses. This is a top-priority incident.",
            "Critical system failure detected on the primary database server. All customer-facing applications are inaccessible, causing a complete halt in order processing and customer support. Revenue is being lost by the minute. Expedited resolution is absolutely necessary. Please escalate immediately.",
            "This is a very long and detailed issue description that requires immediate attention. The system has been experiencing intermittent connectivity problems affecting multiple users across different departments. Users report being unable to access critical business applications and experiencing slow response times. The issue started approximately 2 hours ago and is impacting productivity. Several attempts to restart affected services have been unsuccessful. Network monitoring shows increased latency and packet loss. Please investigate and resolve as this is affecting business operations. Priority level: High. Impact: Organization-wide. Previous troubleshooting steps taken: Service restarts, basic network diagnostics, and user workstation checks.",
        ]
        
        evaluation_results = {}
        
        # 1. Pipeline evaluation
        print("\n🔄 Starting Pipeline Evaluation...")
        pipeline_results = self.classify_with_pipeline(sample_tickets)
        evaluation_results["pipeline"] = pipeline_results
        self.print_results(pipeline_results, "Pipeline Classification Results")
        
        # 2. Custom classifier evaluation
        print("\n🔄 Starting Custom Classifier Evaluation...")
        custom_results = self.classify_with_custom_classifier(sample_queries)
        evaluation_results["custom_classifier"] = custom_results
        self.print_results(custom_results, "Custom Classifier Results")
        
        return evaluation_results


def main():
    """
    Main function to run the evaluation.
    """
    print("🚀 Starting IT Ticket Classification Evaluation")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = ITTicketEvaluator()
    
    # Run comprehensive evaluation
    results = evaluator.run_comprehensive_evaluation()
    
    # Summary
    print("\n📊 Evaluation Summary:")
    for method, method_results in results.items():
        successful = len([r for r in method_results if "error" not in r])
        total = len(method_results)
        print(f"  {method}: {successful}/{total} successful classifications")
    
    print("\n✅ Evaluation completed!")
    return results


if __name__ == "__main__":
    main()