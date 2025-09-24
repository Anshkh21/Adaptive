"""
Performance comparison tests between Node.js and Python backends
"""

import asyncio
import time
import httpx
import json
from typing import Dict, List, Any
import statistics

class PerformanceComparison:
    def __init__(self):
        self.nodejs_url = "http://localhost:5000"
        self.python_url = "http://localhost:8001"
        self.results = {
            "nodejs": {},
            "python": {}
        }
    
    async def test_endpoint_performance(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Dict = None,
        headers: Dict = None
    ) -> Dict[str, Any]:
        """Test performance of a specific endpoint"""
        
        results = {
            "nodejs": {"times": [], "errors": 0, "success_rate": 0},
            "python": {"times": [], "errors": 0, "success_rate": 0}
        }
        
        # Test Node.js backend
        nodejs_times = await self._test_backend(
            f"{self.nodejs_url}{endpoint}",
            method, data, headers, 10
        )
        results["nodejs"] = nodejs_times
        
        # Test Python backend
        python_times = await self._test_backend(
            f"{self.python_url}{endpoint}",
            method, data, headers, 10
        )
        results["python"] = python_times
        
        return results
    
    async def _test_backend(
        self, 
        url: str, 
        method: str, 
        data: Dict, 
        headers: Dict, 
        iterations: int
    ) -> Dict[str, Any]:
        """Test a specific backend"""
        
        times = []
        errors = 0
        
        async with httpx.AsyncClient() as client:
            for i in range(iterations):
                try:
                    start_time = time.time()
                    
                    if method == "GET":
                        response = await client.get(url, headers=headers)
                    elif method == "POST":
                        response = await client.post(url, json=data, headers=headers)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    end_time = time.time()
                    
                    if response.status_code < 400:
                        times.append(end_time - start_time)
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    print(f"Error testing {url}: {e}")
        
        success_rate = ((iterations - errors) / iterations) * 100
        
        return {
            "times": times,
            "errors": errors,
            "success_rate": success_rate,
            "avg_time": statistics.mean(times) if times else 0,
            "min_time": min(times) if times else 0,
            "max_time": max(times) if times else 0,
            "median_time": statistics.median(times) if times else 0
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive performance comparison"""
        
        print("🚀 Starting Performance Comparison Test")
        print("=" * 50)
        
        # Test endpoints
        test_cases = [
            {
                "name": "Health Check",
                "endpoint": "/health",
                "method": "GET"
            },
            {
                "name": "Root Endpoint",
                "endpoint": "/",
                "method": "GET"
            },
            {
                "name": "API Documentation",
                "endpoint": "/docs",
                "method": "GET"
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"\n📊 Testing: {test_case['name']}")
            print("-" * 30)
            
            test_results = await self.test_endpoint_performance(
                test_case["endpoint"],
                test_case["method"]
            )
            
            results[test_case["name"]] = test_results
            
            # Print results
            self._print_test_results(test_case["name"], test_results)
        
        # Generate summary
        summary = self._generate_summary(results)
        self._print_summary(summary)
        
        return {
            "test_results": results,
            "summary": summary
        }
    
    def _print_test_results(self, test_name: str, results: Dict[str, Any]):
        """Print test results for a specific test"""
        
        print(f"Node.js Backend:")
        print(f"  Average Time: {results['nodejs']['avg_time']:.4f}s")
        print(f"  Success Rate: {results['nodejs']['success_rate']:.1f}%")
        print(f"  Errors: {results['nodejs']['errors']}")
        
        print(f"Python Backend:")
        print(f"  Average Time: {results['python']['avg_time']:.4f}s")
        print(f"  Success Rate: {results['python']['success_rate']:.1f}%")
        print(f"  Errors: {results['python']['errors']}")
        
        # Compare performance
        if results['nodejs']['avg_time'] > 0 and results['python']['avg_time'] > 0:
            speed_diff = ((results['python']['avg_time'] - results['nodejs']['avg_time']) / results['nodejs']['avg_time']) * 100
            faster_backend = "Node.js" if speed_diff > 0 else "Python"
            print(f"  🏆 {faster_backend} is {abs(speed_diff):.1f}% faster")
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary"""
        
        nodejs_times = []
        python_times = []
        nodejs_errors = 0
        python_errors = 0
        
        for test_name, test_results in results.items():
            nodejs_times.extend(test_results['nodejs']['times'])
            python_times.extend(test_results['python']['times'])
            nodejs_errors += test_results['nodejs']['errors']
            python_errors += test_results['python']['errors']
        
        summary = {
            "nodejs": {
                "avg_time": statistics.mean(nodejs_times) if nodejs_times else 0,
                "total_errors": nodejs_errors,
                "total_tests": len(nodejs_times)
            },
            "python": {
                "avg_time": statistics.mean(python_times) if python_times else 0,
                "total_errors": python_errors,
                "total_tests": len(python_times)
            }
        }
        
        # Calculate overall winner
        if summary['nodejs']['avg_time'] > 0 and summary['python']['avg_time'] > 0:
            speed_diff = ((summary['python']['avg_time'] - summary['nodejs']['avg_time']) / summary['nodejs']['avg_time']) * 100
            summary['winner'] = "Node.js" if speed_diff > 0 else "Python"
            summary['speed_difference'] = abs(speed_diff)
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print performance summary"""
        
        print("\n" + "=" * 50)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 50)
        
        print(f"Node.js Backend:")
        print(f"  Overall Average Time: {summary['nodejs']['avg_time']:.4f}s")
        print(f"  Total Errors: {summary['nodejs']['total_errors']}")
        print(f"  Total Tests: {summary['nodejs']['total_tests']}")
        
        print(f"\nPython Backend:")
        print(f"  Overall Average Time: {summary['python']['avg_time']:.4f}s")
        print(f"  Total Errors: {summary['python']['total_errors']}")
        print(f"  Total Tests: {summary['python']['total_tests']}")
        
        if 'winner' in summary:
            print(f"\n🏆 Overall Winner: {summary['winner']}")
            print(f"   Speed Difference: {summary['speed_difference']:.1f}%")
        
        print("\n💡 Recommendations:")
        if summary['nodejs']['avg_time'] < summary['python']['avg_time']:
            print("   - Node.js shows better raw performance")
            print("   - Consider Node.js for high-throughput scenarios")
        else:
            print("   - Python shows competitive performance")
            print("   - Consider Python for complex AI/ML features")
        
        print("   - Both backends are production-ready")
        print("   - Choose based on team expertise and feature requirements")

async def main():
    """Main function to run performance comparison"""
    
    print("🔬 Adaptive Assessment Platform - Performance Comparison")
    print("Node.js vs Python Backend")
    print("=" * 60)
    
    # Check if both backends are running
    try:
        async with httpx.AsyncClient() as client:
            # Test Node.js
            try:
                response = await client.get("http://localhost:5000/health", timeout=5.0)
                print("✅ Node.js backend is running")
            except:
                print("❌ Node.js backend is not running on port 5000")
                return
            
            # Test Python
            try:
                response = await client.get("http://localhost:8001/health", timeout=5.0)
                print("✅ Python backend is running")
            except:
                print("❌ Python backend is not running on port 8001")
                return
                
    except Exception as e:
        print(f"❌ Error checking backends: {e}")
        return
    
    # Run performance comparison
    comparison = PerformanceComparison()
    results = await comparison.run_comprehensive_test()
    
    # Save results to file
    with open("performance_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: performance_results.json")

if __name__ == "__main__":
    asyncio.run(main())
