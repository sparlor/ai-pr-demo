#!/usr/bin/env python3
"""
AI PR Review script using AWS Bedrock and GitHub Actions
"""

import sys
import json
import boto3
import os

def read_diff_file(file_path):
    """Read and truncate the diff file to 40k characters"""
    try:
        with open(file_path, 'r') as f:
            diff_content = f.read()
        
        # Limit to 40k characters
        if len(diff_content) > 40000:
            diff_content = diff_content[:40000]
            print("⚠️  Diff truncated to 40,000 characters", file=sys.stderr)
        
        return diff_content
    except FileNotFoundError:
        print(f"Error: Diff file '{file_path}' not found", file=sys.stderr)
        sys.exit(1)

def create_review_prompt(diff_content):
    """Create a structured DevOps review prompt"""
    prompt = f"""You are an expert DevOps and infrastructure engineer. Review the following code diff and provide a structured analysis.

Please analyze the following aspects:
1. **Infrastructure & Cloud**: Any AWS/cloud resource changes, best practices, security implications
2. **Code Quality**: Code standards, patterns, potential bugs, error handling
3. **Security**: Security vulnerabilities, credential exposure, IAM permissions, encryption
4. **Performance**: Performance implications, scalability concerns, resource optimization
5. **DevOps Practices**: CI/CD, automation, monitoring, logging considerations
6. **Recommendations**: Specific actionable improvements (prioritized by importance)

Code Diff:
```
{diff_content}
```

Provide your review in a clear, concise format with specific feedback and actionable recommendations."""
    
    return prompt

def invoke_bedrock_model(prompt):
    """Invoke AWS Bedrock model for code review using Amazon Nova."""
    try:
        region = os.getenv("AWS_REGION", "us-east-1")
        client = boto3.client("bedrock-runtime", region_name=region)

        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0").strip()

        print(f"DEBUG: AWS_REGION={region}", file=sys.stderr)
        print(f"DEBUG: BEDROCK_MODEL_ID={model_id}", file=sys.stderr)

        # ✅ Nova: messages-style schema (NO textGenerationConfig)
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1200,
                "temperature": 0.2,
                "topP": 0.9
            }
        }

        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json",
        )

        result = json.loads(response["body"].read().decode("utf-8"))

        # Extract text (common pattern)
        output = result.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        text_parts = [c.get("text", "") for c in content if isinstance(c, dict)]
        review_text = "\n".join([t for t in text_parts if t]).strip()

        return review_text if review_text else json.dumps(result)

    except Exception as e:
        print(f"Error invoking Bedrock: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python review.py <diff_file>", file=sys.stderr)
        sys.exit(1)
    
    diff_file = sys.argv[1]
    
    # Read the diff file
    diff_content = read_diff_file(diff_file)
    
    if not diff_content.strip():
        print("## AI PR Review\n\nNo changes found in diff file", flush=True)
        sys.exit(0)
    
    # Create the review prompt
    prompt = create_review_prompt(diff_content)
    
    # Invoke Bedrock for review
    print("Running AI review with Bedrock...", file=sys.stderr)
    review = invoke_bedrock_model(prompt)
    
    # Output review directly to stdout (will be captured by workflow)
    print(review, flush=True)
    
    print("✅ Review completed successfully", file=sys.stderr)

if __name__ == '__main__':
    main()
