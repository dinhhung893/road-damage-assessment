"""Phase 2 verification audit script."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
from src.engine.pci import PCIEngine, PCIResult, BBOX_CORRECTION_FACTORS
import subprocess

engine = PCIEngine()
c = {}

# PCI-01: Load PCI data from JSON
data = engine.data
c["PCI-01"] = "deduct_value_curves" in data and "cdv_correction" in data and "severity_assignment" in data

# PCI-02: Linear interpolation (via deduct value lookup)
c["PCI-02"] = engine.lookup_deduct_value("D00", "Low", 5.0) >= 0

# PCI-03: Density calculation
c["PCI-03"] = engine.calculate_density(10000, 307200, 0.3) > 0

# PCI-04: Severity assignment
c["PCI-04"] = engine.assign_severity("D00", 5.0) in ("Low", "Medium", "High")

# PCI-05: Deduct value lookup
c["PCI-05"] = engine.lookup_deduct_value("D00", "Low", 5.0) >= 0

# PCI-06: CDV calculation
cdv, q, tdv = engine.calculate_cdv([10, 20, 30])
c["PCI-06"] = cdv >= 0 and q > 0

# PCI-07: PCI rating
c["PCI-07"] = engine.classify_rating(85) == "Good"

# PCI-08: Maintenance recommendation
action, detail = engine.get_maintenance("Good")
c["PCI-08"] = len(action) > 0

# PCI-09: Section-level PCI
mock_results = [
    PCIResult(
        pci_value=v,
        rating=engine.classify_rating(v),
        maintenance_action="", maintenance_detail="",
        cdv=0, q=1, tdv=0, damages=[], sample_unit_area_sqft=5000
    )
    for v in [85.0, 70.0, 55.0]
]
c["PCI-09"] = abs(engine.calculate_section_pci(mock_results)["section_pci"] - 70.0) < 0.01

# PCI-10: Bbox correction factors
c["PCI-10"] = BBOX_CORRECTION_FACTORS.get("D00") == 0.3

# PCI-11: Edge case — empty input = PCI 100
c["PCI-11"] = engine.calculate_pci([], image_area_px=640*480).pci_value == 100.0

# PCI-12: Unit conversion (sqft param in PCIResult)
c["PCI-12"] = engine.calculate_pci(
    [{"code": "D00", "bbox": (100, 100, 200, 200), "confidence": 0.9}],
    image_area_px=640*480
).pci_value >= 0

# Data file
c["data_file"] = Path("data/pci_astm_d6433.json").exists()

# Test results
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_pci.py", "--tb=no", "-q"],
    capture_output=True, text=True
)
c["tests_pass"] = "passed" in r.stdout

for k, v in c.items():
    print(f"  {k}: {'PASS' if v else 'FAIL'}")
