#!/usr/bin/env python3
"""
Generate DIM_COMPLIANCE_FRAMEWORKS reference data.

This is static reference data with exactly 8 compliance frameworks
that Phantom Sec customers typically adopt.
"""

import json
from typing import List, Dict, Any

def generate_compliance_frameworks() -> List[Dict[str, Any]]:
    """Generate the 8 compliance framework records with all attributes."""
    
    frameworks = [
        {
            "framework_id": 1,
            "framework_name": "SOC2_Type_I",
            "framework_category": "security_audit",
            "complexity_score": 4,
            "avg_completion_days": 90,
            "industry_relevance": "all_industries",
            "geographic_scope": "global",
            "automation_percentage": 75,
            "annual_audit_required": False,
            "certification_cost_usd": 25000
        },
        {
            "framework_id": 2,
            "framework_name": "SOC2_Type_II",
            "framework_category": "security_audit",
            "complexity_score": 7,
            "avg_completion_days": 180,
            "industry_relevance": "all_industries",
            "geographic_scope": "global",
            "automation_percentage": 65,
            "annual_audit_required": True,
            "certification_cost_usd": 45000
        },
        {
            "framework_id": 3,
            "framework_name": "ISO27001",
            "framework_category": "security_management",
            "complexity_score": 8,
            "avg_completion_days": 240,
            "industry_relevance": "all_industries",
            "geographic_scope": "global",
            "automation_percentage": 60,
            "annual_audit_required": True,
            "certification_cost_usd": 35000
        },
        {
            "framework_id": 4,
            "framework_name": "HIPAA",
            "framework_category": "healthcare_privacy",
            "complexity_score": 6,
            "avg_completion_days": 150,
            "industry_relevance": "healthtech",
            "geographic_scope": "usa",
            "automation_percentage": 70,
            "annual_audit_required": False,
            "certification_cost_usd": 15000
        },
        {
            "framework_id": 5,
            "framework_name": "GDPR",
            "framework_category": "data_privacy",
            "complexity_score": 7,
            "avg_completion_days": 120,
            "industry_relevance": "all_industries",
            "geographic_scope": "eu_global",
            "automation_percentage": 55,
            "annual_audit_required": False,
            "certification_cost_usd": 20000
        },
        {
            "framework_id": 6,
            "framework_name": "PCI_DSS",
            "framework_category": "payment_security",
            "complexity_score": 5,
            "avg_completion_days": 90,
            "industry_relevance": "ecommerce_fintech",
            "geographic_scope": "global",
            "automation_percentage": 80,
            "annual_audit_required": True,
            "certification_cost_usd": 30000
        },
        {
            "framework_id": 7,
            "framework_name": "FedRAMP",
            "framework_category": "government_cloud",
            "complexity_score": 9,
            "avg_completion_days": 365,
            "industry_relevance": "government_contractors",
            "geographic_scope": "usa",
            "automation_percentage": 45,
            "annual_audit_required": True,
            "certification_cost_usd": 150000
        },
        {
            "framework_id": 8,
            "framework_name": "NIST_CSF",
            "framework_category": "cybersecurity_framework",
            "complexity_score": 6,
            "avg_completion_days": 180,
            "industry_relevance": "all_industries",
            "geographic_scope": "usa_global",
            "automation_percentage": 70,
            "annual_audit_required": False,
            "certification_cost_usd": 25000
        }
    ]
    
    return frameworks

def validate_frameworks(frameworks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate the framework data for consistency."""
    
    validation_results = {
        "total_frameworks": len(frameworks),
        "unique_ids": len(set(f["framework_id"] for f in frameworks)),
        "unique_names": len(set(f["framework_name"] for f in frameworks)),
        "categories": list(set(f["framework_category"] for f in frameworks)),
        "industry_relevance_types": list(set(f["industry_relevance"] for f in frameworks)),
        "geographic_scopes": list(set(f["geographic_scope"] for f in frameworks)),
        "complexity_range": (
            min(f["complexity_score"] for f in frameworks),
            max(f["complexity_score"] for f in frameworks)
        ),
        "completion_days_range": (
            min(f["avg_completion_days"] for f in frameworks),
            max(f["avg_completion_days"] for f in frameworks)
        ),
        "automation_range": (
            min(f["automation_percentage"] for f in frameworks),
            max(f["automation_percentage"] for f in frameworks)
        ),
        "cost_range": (
            min(f["certification_cost_usd"] for f in frameworks),
            max(f["certification_cost_usd"] for f in frameworks)
        ),
        "annual_audit_required_count": sum(1 for f in frameworks if f["annual_audit_required"])
    }
    
    return validation_results

def print_framework_summary(frameworks: List[Dict[str, Any]]) -> None:
    """Print a summary of the frameworks for verification."""
    
    print("📊 COMPLIANCE FRAMEWORKS SUMMARY")
    print("=" * 80)
    print(f"{'ID':<4} {'Name':<15} {'Category':<25} {'Complexity':<12} {'Days':<6} {'Cost':<10}")
    print("-" * 80)
    
    for f in frameworks:
        print(f"{f['framework_id']:<4} "
              f"{f['framework_name']:<15} "
              f"{f['framework_category']:<25} "
              f"{f['complexity_score']:<12} "
              f"{f['avg_completion_days']:<6} "
              f"${f['certification_cost_usd']:,}")
    
    print("\n📈 USA ADOPTION PATTERNS (from GAMEPLAN.md):")
    print("- SOC2_Type_I: 95% of all companies")
    print("- SOC2_Type_II: 70% of all companies")
    print("- ISO27001: 40% of all companies")
    print("- HIPAA: 95% if healthtech, 5% others")
    print("- GDPR: 35% of all companies")
    print("- PCI_DSS: 90% if ecommerce/fintech, 15% others")
    print("- FedRAMP: 80% if government_contractors, 2% others")
    print("- NIST_CSF: 75% of all companies")

def main():
    print("🏗️  Generating DIM_COMPLIANCE_FRAMEWORKS reference data...")
    
    # Generate frameworks
    frameworks = generate_compliance_frameworks()
    
    # Validate data
    print("\n✅ Validating framework data...")
    validation = validate_frameworks(frameworks)
    
    print(f"\nValidation Results:")
    print(f"  Total frameworks: {validation['total_frameworks']}")
    print(f"  Unique IDs: {validation['unique_ids']}")
    print(f"  Unique names: {validation['unique_names']}")
    print(f"  Categories: {', '.join(validation['categories'])}")
    print(f"  Industry relevance: {', '.join(validation['industry_relevance_types'])}")
    print(f"  Geographic scopes: {', '.join(validation['geographic_scopes'])}")
    print(f"  Complexity range: {validation['complexity_range'][0]}-{validation['complexity_range'][1]}")
    print(f"  Completion days: {validation['completion_days_range'][0]}-{validation['completion_days_range'][1]} days")
    print(f"  Automation %: {validation['automation_range'][0]}-{validation['automation_range'][1]}%")
    print(f"  Cost range: ${validation['cost_range'][0]:,}-${validation['cost_range'][1]:,}")
    print(f"  Frameworks requiring annual audit: {validation['annual_audit_required_count']}")
    
    # Print summary
    print("\n")
    print_framework_summary(frameworks)
    
    # Save to file
    output_file = "DIM_COMPLIANCE_FRAMEWORKS.json"
    with open(output_file, 'w') as f:
        json.dump(frameworks, f, indent=2)
    
    print(f"\n💾 Saved {len(frameworks)} frameworks to {output_file}")
    print("✨ DIM_COMPLIANCE_FRAMEWORKS generation complete!")

if __name__ == "__main__":
    main()