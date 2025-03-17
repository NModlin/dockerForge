#!/usr/bin/env python3
"""
Test script for DockerForge Phase 3 functionality.

This script demonstrates the key features of the log monitoring and analysis system:
1. Log collection
2. Pattern recognition
3. Log analysis
4. Issue detection
5. Recommendation generation
"""

import os
import sys
import time
import json
import docker
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.monitoring.log_collector import get_log_collection_manager
from src.monitoring.pattern_recognition import get_pattern_recognition_engine
from src.monitoring.log_analyzer import get_log_analyzer
from src.monitoring.issue_detector import get_issue_detector
from src.monitoring.recommendation_engine import get_recommendation_engine
from src.monitoring.log_explorer import get_log_explorer


def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)


def start_test_container():
    """Start a test container that generates logs with errors."""
    print_header("Starting Test Container")
    
    try:
        # Connect to Docker
        client = docker.from_env()
        
        # Check if container already exists
        try:
            container = client.containers.get("dockerforge-test")
            print(f"Container already exists with status: {container.status}")
            
            # Remove if not running
            if container.status != "running":
                container.remove(force=True)
                print("Removed existing container")
                container = None
            else:
                return container
        except docker.errors.NotFound:
            container = None
        
        # Create container with a script that generates logs with errors
        print("Creating test container...")
        container = client.containers.run(
            "alpine:latest",
            name="dockerforge-test",
            command=[
                "sh", "-c",
                """
                echo "Starting test container..."
                echo "This is a normal log message"
                echo "This is another normal log message"
                
                # Generate some error patterns
                echo "Error from daemon: connection refused"
                sleep 1
                echo "WARNING: Connection timed out"
                sleep 1
                echo "ERROR: Permission denied: /var/lib/data"
                sleep 1
                echo "No such file or directory: /etc/config.json"
                sleep 1
                echo "Out of memory: Killed process 123"
                sleep 1
                
                # Generate more logs
                for i in $(seq 1 10); do
                    echo "Processing item $i"
                    if [ $i -eq 5 ]; then
                        echo "ERROR: Failed to process item $i"
                    fi
                    sleep 0.5
                done
                
                echo "Container is now running and will continue to generate logs..."
                
                # Keep container running and generate periodic logs
                while true; do
                    echo "Heartbeat $(date)"
                    sleep 10
                    
                    # Randomly generate errors
                    RANDOM_NUM=$((RANDOM % 10))
                    if [ $RANDOM_NUM -eq 0 ]; then
                        echo "ERROR: Database connection failed"
                    elif [ $RANDOM_NUM -eq 1 ]; then
                        echo "WARNING: High CPU usage detected"
                    elif [ $RANDOM_NUM -eq 2 ]; then
                        echo "ERROR: API request failed with status code 500"
                    fi
                done
                """
            ],
            detach=True,
        )
        
        print(f"Container started with ID: {container.id}")
        
        # Wait for container to generate some logs
        print("Waiting for container to generate logs...")
        time.sleep(5)
        
        return container
    
    except Exception as e:
        print(f"Error starting test container: {str(e)}")
        sys.exit(1)


def test_log_collection(container):
    """Test log collection functionality."""
    print_header("Testing Log Collection")
    
    try:
        # Get log collection manager
        log_collection_manager = get_log_collection_manager()
        
        # Start log collection
        if not log_collection_manager.running:
            log_collection_manager.start()
            print("Started log collection")
        
        # Wait for logs to be collected
        print("Waiting for logs to be collected...")
        time.sleep(5)
        
        # Get logs for the container
        logs = log_collection_manager.get_container_logs(
            container_id=container.id,
            limit=10,
        )
        
        print(f"Collected {len(logs)} logs from container")
        
        # Print some logs
        print("\nSample logs:")
        for i, log in enumerate(logs[-5:]):
            print(f"{i+1}. {log}")
        
        return logs
    
    except Exception as e:
        print(f"Error testing log collection: {str(e)}")
        return []


def test_pattern_recognition(logs):
    """Test pattern recognition functionality."""
    print_header("Testing Pattern Recognition")
    
    try:
        # Get pattern recognition engine
        pattern_recognition_engine = get_pattern_recognition_engine()
        
        # Process logs for pattern matches
        all_matches = []
        for log in logs:
            matches = pattern_recognition_engine.process_log(log)
            all_matches.extend(matches)
        
        print(f"Found {len(all_matches)} pattern matches")
        
        # Print pattern matches
        if all_matches:
            print("\nPattern matches:")
            for i, match in enumerate(all_matches):
                pattern = pattern_recognition_engine.get_pattern(match.pattern_id)
                print(f"{i+1}. Pattern: {pattern.name} (Severity: {pattern.severity})")
                print(f"   Match: {match.match_text}")
                print(f"   Log: {match.log_entry}")
                print()
        
        return all_matches
    
    except Exception as e:
        print(f"Error testing pattern recognition: {str(e)}")
        return []


def test_log_analysis(container):
    """Test log analysis functionality."""
    print_header("Testing Log Analysis")
    
    try:
        # Get log analyzer
        log_analyzer = get_log_analyzer()
        
        # Analyze container logs
        print("Analyzing container logs...")
        try:
            analysis = log_analyzer.analyze_container_logs(
                container_id=container.id,
                template_id="default",
                confirm_cost=False,  # Skip cost confirmation for testing
            )
            
            print(f"Analysis completed with {len(analysis.issues)} issues and {len(analysis.recommendations)} recommendations")
            
            # Print analysis summary
            print("\nAnalysis Summary:")
            print(analysis.summary)
            
            # Print issues
            if analysis.issues:
                print("\nIssues:")
                for i, issue in enumerate(analysis.issues):
                    print(f"{i+1}. {issue.get('title', 'Untitled Issue')} (Severity: {issue.get('severity', 'unknown')})")
                    print(f"   {issue.get('description', '')}")
            
            # Print recommendations
            if analysis.recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(analysis.recommendations):
                    print(f"{i+1}. {rec.get('title', 'Untitled Recommendation')}")
                    print(f"   {rec.get('description', '')}")
            
            return analysis
        
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            print("Skipping analysis step...")
            return None
    
    except Exception as e:
        print(f"Error testing log analysis: {str(e)}")
        return None


def test_issue_detection(container, pattern_matches):
    """Test issue detection functionality."""
    print_header("Testing Issue Detection")
    
    try:
        # Get issue detector
        issue_detector = get_issue_detector()
        
        # Get issues for the container
        issues = issue_detector.get_container_issues(container.id)
        
        print(f"Found {len(issues)} issues for container")
        
        # Print issues
        if issues:
            print("\nIssues:")
            for i, issue in enumerate(issues):
                print(f"{i+1}. {issue.title} (Severity: {issue.severity.value}, Status: {issue.status.value})")
                print(f"   {issue.description}")
                print()
        
        # If no issues found, create a manual issue
        if not issues and pattern_matches:
            # Use the first pattern match to create an issue
            match = pattern_matches[0]
            pattern = get_pattern_recognition_engine().get_pattern(match.pattern_id)
            
            print("Creating a manual issue...")
            issue = issue_detector.create_issue_manual(
                container_id=container.id,
                container_name=match.log_entry.container_name,
                title=f"Manual: {pattern.name}",
                description=pattern.description,
                severity=pattern.severity,
                tags=["manual", "test"],
            )
            
            print(f"Created manual issue: {issue.title}")
            issues = [issue]
        
        return issues
    
    except Exception as e:
        print(f"Error testing issue detection: {str(e)}")
        return []


def test_recommendation_generation(issues):
    """Test recommendation generation functionality."""
    print_header("Testing Recommendation Generation")
    
    try:
        # Get recommendation engine
        recommendation_engine = get_recommendation_engine()
        
        all_recommendations = []
        
        # Generate recommendations for issues
        for issue in issues:
            print(f"Generating recommendation for issue: {issue.title}")
            
            try:
                # Try to create recommendation from pattern first
                recommendation = recommendation_engine.create_recommendation_from_pattern(issue.id)
                
                if not recommendation:
                    # If no pattern-based recommendation, create a manual one
                    print("No pattern-based recommendation available, creating manual recommendation...")
                    recommendation = recommendation_engine.create_recommendation_manual(
                        issue_id=issue.id,
                        title=f"Recommendation for {issue.title}",
                        description=f"This is a manual recommendation for resolving the issue: {issue.title}",
                        steps=[
                            {
                                "description": "Check container logs for more details",
                                "command": f"docker logs {issue.container_id}",
                                "verification": "Look for specific error messages in the logs"
                            },
                            {
                                "description": "Restart the container",
                                "command": f"docker restart {issue.container_id}",
                                "verification": "Verify that the container is running with 'docker ps'"
                            }
                        ],
                        tags=["manual", "test"],
                    )
                
                print(f"Created recommendation: {recommendation.title}")
                all_recommendations.append(recommendation)
                
                # Print recommendation details
                print(f"\nRecommendation: {recommendation.title}")
                print(f"Description: {recommendation.description}")
                
                if recommendation.steps:
                    print("Steps:")
                    for i, step in enumerate(recommendation.steps):
                        print(f"{i+1}. {step.description}")
                        if step.command:
                            print(f"   Command: {step.command}")
                        if step.verification:
                            print(f"   Verification: {step.verification}")
            
            except Exception as e:
                print(f"Error generating recommendation for issue {issue.id}: {str(e)}")
        
        return all_recommendations
    
    except Exception as e:
        print(f"Error testing recommendation generation: {str(e)}")
        return []


def test_log_explorer(container):
    """Test log explorer functionality."""
    print_header("Testing Log Explorer")
    
    try:
        # Get log explorer
        log_explorer = get_log_explorer()
        
        # Search logs
        print("Searching logs for 'error'...")
        search_result = log_explorer.search_logs(
            query="error",
            container_ids=[container.id],
            case_sensitive=False,
        )
        
        print(f"Found {search_result.total_matches} logs containing 'error'")
        
        # Get log statistics
        print("\nGenerating log statistics...")
        try:
            stats = log_explorer.get_log_statistics(container_id=container.id)
            
            print(f"Log count: {stats.log_count}")
            print(f"Error count: {stats.error_count}")
            print(f"Warning count: {stats.warning_count}")
            
            # Print common terms
            print("\nCommon terms:")
            for term, count in stats.common_terms[:5]:
                print(f"- {term}: {count}")
        
        except Exception as e:
            print(f"Error generating statistics: {str(e)}")
        
        # Get log timeline
        print("\nGenerating log timeline...")
        try:
            timeline = log_explorer.get_log_timeline(
                container_id=container.id,
                interval="minute",
            )
            
            print(f"Timeline entries: {len(timeline)}")
            for time_key, count in list(timeline.items())[:5]:
                print(f"- {time_key}: {count} logs")
        
        except Exception as e:
            print(f"Error generating timeline: {str(e)}")
    
    except Exception as e:
        print(f"Error testing log explorer: {str(e)}")


def main():
    """Main function to run the tests."""
    print_header("DockerForge Phase 3 Test")
    
    # Start test container
    container = start_test_container()
    
    # Test log collection
    logs = test_log_collection(container)
    
    # Test pattern recognition
    pattern_matches = test_pattern_recognition(logs)
    
    # Test issue detection
    issues = test_issue_detection(container, pattern_matches)
    
    # Test recommendation generation
    recommendations = test_recommendation_generation(issues)
    
    # Test log analysis
    analysis = test_log_analysis(container)
    
    # Test log explorer
    test_log_explorer(container)
    
    print_header("Test Complete")
    print(f"Container ID: {container.id}")
    print(f"Container Name: {container.name}")
    print(f"Logs Collected: {len(logs)}")
    print(f"Pattern Matches: {len(pattern_matches)}")
    print(f"Issues Detected: {len(issues)}")
    print(f"Recommendations Generated: {len(recommendations)}")
    
    print("\nThe test container will continue running in the background.")
    print("To stop and remove it, run: docker rm -f dockerforge-test")


if __name__ == "__main__":
    main()
