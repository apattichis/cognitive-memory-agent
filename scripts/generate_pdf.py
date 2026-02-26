"""Generate the expanded Zeltron Corporation manual (5 pages).

Run: python scripts/generate_pdf.py
Output: data/zeltron_manual.pdf
"""

import os, sys
from fpdf import FPDF

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "zeltron_manual.pdf")


def build_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Page 1: Company Overview ──────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "ZELTRON CORPORATION", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 7, "Confidential Corporate Manual - 2024 Edition", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Section 1: Company Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)

    text = (
        "Zeltron Corporation was founded in 2019 in Reykjavik, Iceland by Dr. Maren Solvik "
        "(quantum physicist, University of Copenhagen) and Tomas Ekberg (acoustic engineer, "
        "formerly Ericsson Research). The company motto is 'In Resonance, Truth.' Zeltron "
        "trades on the Iceland Stock Exchange under the ticker ZLTN.\n\n"
        "Zeltron pioneered quantum-acoustic computing, a paradigm that exploits sound wave "
        "interference patterns in crystalline substrates to perform matrix operations at "
        "room temperature - eliminating the cryogenic cooling required by traditional quantum "
        "computers.\n\n"
        "As of December 2024 the company employs 342 people across three offices: Reykjavik "
        "(headquarters and manufacturing), Zurich (sales and finance), and Osaka (hardware "
        "R&D). Total 2024 revenue was approximately $89 million USD, distributed as follows:\n\n"
        "  - Defense & Government Contracts (NATO, ESA): 52% ($46.3M)\n"
        "  - Enterprise Processor Licensing: 31% ($27.6M)\n"
        "  - Research Grants & Academic Partnerships: 11% ($9.8M)\n"
        "  - Harmonic Language Tooling & Support: 6% ($5.3M)\n\n"
        "Board of Directors:\n"
        "  - Dr. Maren Solvik (Chair & CTO) - PhD Copenhagen, 14 patents in acoustic resonance\n"
        "  - Tomas Ekberg (CEO) - 20 years at Ericsson, led mobile baseband division\n"
        "  - Ingrid Hakansson (CFO) - former Goldman Sachs VP, joined Zeltron 2021\n"
        "  - Prof. Kenji Yamamoto (Independent Director) - Osaka University, piezoelectric "
        "materials expert\n"
        "  - Dr. Astrid Lindqvist (Independent Director) - ex-DARPA program manager, "
        "quantum computing policy"
    )
    pdf.multi_cell(0, 5, text)

    # ── Page 2: QA-7 Technical Specifications ─────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Section 2: QA-7 Technical Specifications", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)

    text = (
        "The QA-7 is Zeltron's flagship quantum-acoustic processor. It achieves 847 "
        "teraflops using 12,847 barium titanate resonators arranged in a proprietary "
        "Fibonacci Spiral Configuration. The resonators operate at a base frequency of "
        "440 Hz (concert A) and scale up to 88,000 Hz through harmonic overtone layers.\n\n"
        "The processor operates at the Solvik Temperature of 22.4 degrees Celsius, named "
        "after Dr. Maren Solvik who discovered the optimal thermal operating point for "
        "barium titanate acoustic resonance. This eliminates the need for cryogenic "
        "cooling, a key advantage over competing platforms.\n\n"
        "Version History:\n"
        "  - QA-3 (2021): First commercial processor, 128 teraflops, 2,048 resonators, "
        "single-layer spiral\n"
        "  - QA-5 (2023): 410 teraflops, 6,400 resonators, dual-layer Fibonacci spiral, "
        "first NATO deployment\n"
        "  - QA-7 (2024): 847 teraflops, 12,847 resonators, triple-layer spiral, Solvik "
        "Temperature calibration\n\n"
        "Physical Specifications:\n"
        "  - Dimensions: 48cm x 48cm x 12cm (rack-mountable, 3U)\n"
        "  - Weight: 14.2 kg\n"
        "  - Power consumption: 2.8 kW (idle), 4.1 kW (peak load)\n"
        "  - Cooling: Closed-loop glycol system, maintains 22.4C +/- 0.05C\n"
        "  - Interconnect: 4x 400GbE optical, 2x PCIe 6.0 x16\n\n"
        "The QA-7 factored a 2048-bit RSA key in 14.7 seconds during a supervised trial "
        "(report ZR-2024-0871), making it the fastest known non-cryogenic factoring system.\n\n"
        "See Section 5 (Competitive Landscape) for benchmark comparisons with WaveLogic, "
        "NovaSonic, and AcoustiQ processors."
    )
    pdf.multi_cell(0, 5, text)

    # ── Page 3: Research & Programming ────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Section 3: Research & Programming", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)

    text = (
        "Zeltron's R&D is organized into three divisions:\n\n"
        "  1. Resonance Engineering (RE) - Hardware design, resonator fabrication, thermal "
        "management. Based primarily in Osaka. Head: Dr. Yuki Tanaka.\n"
        "  2. Acoustic Logic (AL) - Algorithm design, signal processing architectures, "
        "benchmark development. Based in Reykjavik. Head: Dr. Erik Jonasson.\n"
        "  3. Harmonic Systems (HS) - Programming language development, compiler toolchain, "
        "developer relations. Based in Reykjavik. Head: Freya Olsen.\n\n"
        "The Harmonic Programming Language:\n"
        "Zeltron developed Harmonic, a domain-specific language for quantum-acoustic "
        "computing. Key constructs use musical terminology:\n"
        "  - crescendo: for-loop (iteratively increasing computation)\n"
        "  - fermata: conditional/wait (pause until condition met)\n"
        "  - staccato: parallel dispatch (short, independent tasks)\n"
        "  - legato: pipelined operations (smooth data flow)\n"
        "Harmonic compiles to WaveIR, an intermediate representation that maps directly "
        "to resonator activation patterns. The compiler (hmc v3.2) supports ahead-of-time "
        "and JIT compilation modes.\n\n"
        "Active Research Projects:\n"
        "  - Project Crescendo (2024-present): Next-generation resonator materials. "
        "Exploring lithium tantalate and lead zirconate titanate (PZT) as alternatives "
        "to barium titanate. Goal: 30% higher Q-factor.\n"
        "  - Project Fermata (2023-2025): Fault-tolerant acoustic computing. Developing "
        "error correction codes for resonator drift. Published 3 papers at ISCA 2024.\n\n"
        "Academic Collaboration:\n"
        "Zeltron maintains a formal research partnership with the University of Reykjavik "
        "(established 2022). Key collaborators include Prof. Bjorn Magnusson (acoustic "
        "physics) and Dr. Sigrun Helgadottir (compiler design). Joint publications: 7 "
        "papers (4 in IEEE Transactions on Quantum Engineering, 2 at ISCA, 1 at MICRO). "
        "The partnership produced 12 MSc theses and 3 PhD candidates as of 2024.\n\n"
        "Internal Metrics (2024):\n"
        "  - Lines of Harmonic code in production: 847,000\n"
        "  - Internal benchmark suite: 312 test cases (AcousticBench v2.1)\n"
        "  - Compiler bugs fixed: 1,247 (hmc v3.0 to v3.2)\n"
        "  - Developer community: 2,100 registered Harmonic developers worldwide"
    )
    pdf.multi_cell(0, 5, text)

    # ── Page 4: Organization & Operations ─────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Section 4: Organization & Operations", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)

    text = (
        "Employee Rank System (musical terminology):\n"
        "  - Pianissimo (Junior, 0-2 years): Entry-level engineers and analysts. "
        "Salary band: $65,000 - $85,000\n"
        "  - Mezzo (Mid-level, 2-5 years): Independent contributors and project leads. "
        "Salary band: $90,000 - $130,000\n"
        "  - Fortissimo (Senior, 5-10 years): Technical architects and team leads. "
        "Salary band: $135,000 - $180,000\n"
        "  - Sforzando (Principal, 10+ years): Division-level technical authority. "
        "Salary band: $185,000 - $240,000\n"
        "  - Conductor (Executive): C-suite and VP-level leadership. "
        "Salary band: $250,000 - $400,000 + equity\n\n"
        "Office Details:\n"
        "  - Reykjavik (HQ): 180 employees. Houses executive leadership, Acoustic Logic "
        "division, Harmonic Systems division, and the main QA-7 manufacturing cleanroom. "
        "Building: Tonholl Center, 4,200 sqm.\n"
        "  - Zurich: 87 employees. Sales, enterprise partnerships, finance, legal, and "
        "European government relations. Building: Bahnhofstrasse 42, leased.\n"
        "  - Osaka: 75 employees. Resonance Engineering division, advanced materials lab, "
        "hardware prototyping. Building: Osaka Innovation Hub, 2,100 sqm.\n\n"
        "Financial Note:\n"
        "Total 2024 revenue reached $91.2 million USD when including deferred contract "
        "obligations and multi-year license prepayments recognized in Q4. The base "
        "operational revenue figure (excluding deferred items) was $89 million as reported "
        "in Section 1. The $2.2 million difference consists of a 3-year NATO maintenance "
        "contract ($1.4M) and prepaid Harmonic enterprise licenses ($0.8M). Audited "
        "financials are filed with the Icelandic Financial Supervisory Authority (FME) "
        "under registration ISK-2019-4471."
    )
    pdf.multi_cell(0, 5, text)

    # ── Page 5: Competitive Landscape & Incidents ─────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Section 5: Competitive Landscape & Incidents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)

    text = (
        "Key Competitors:\n\n"
        "1. WaveLogic Inc. (Singapore)\n"
        "   Founded 2020. Flagship: SonicCore 3 processor, 203 teraflops. Uses lithium "
        "niobate resonators (7,200 units). Requires active cooling to 18C. Primary market: "
        "financial services (high-frequency trading). 2024 revenue: ~$34M. CEO: Dr. Wei "
        "Chen. 156 employees.\n\n"
        "2. NovaSonic GmbH (Munich, Germany)\n"
        "   Founded 2022 (spin-off from Fraunhofer Institute). Flagship: AkustikPro 1, "
        "89 teraflops. Uses zinc oxide thin-film resonators (3,100 units). Room temperature "
        "operation but limited to signal processing workloads. 2024 revenue: ~$12M. "
        "CEO: Dr. Klaus Richter. 64 employees. Backed by BMW Ventures and Siemens Energy.\n\n"
        "3. AcoustiQ Ltd. (Tel Aviv, Israel)\n"
        "   Founded 2021. Flagship: QWave Mark II, 312 teraflops. Uses aluminum nitride "
        "MEMS resonators (9,400 units). Operating temperature: 20C (active cooling). "
        "Primary market: defense and intelligence (signals processing, cryptanalysis). "
        "2024 revenue: ~$28M. CEO: Col. (ret.) Yael Avidan. 112 employees. Close ties "
        "to Israeli Defense Forces Unit 8200.\n\n"
        "Benchmark Comparison (2024, RSA-2048 factoring):\n"
        "  - Zeltron QA-7: 14.7 seconds\n"
        "  - AcoustiQ QWave Mark II: 58.3 seconds\n"
        "  - WaveLogic SonicCore 3: 142.9 seconds\n"
        "  - NovaSonic AkustikPro 1: unable to complete (insufficient compute)\n\n"
        "The 2024 Reykjavik Incident:\n"
        "On March 15, 2024, during a live NATO procurement demonstration at the Tonholl "
        "Center, the QA-7 prototype experienced a 3-hour system outage. Root cause analysis "
        "(internal report ZR-INC-2024-003) determined that the ambient temperature in the "
        "demonstration hall reached 22.7C - exceeding the Solvik Temperature of 22.4C by "
        "0.3 degrees. This caused resonator frequency drift in the outer spiral layer, "
        "producing cascading phase errors. The glycol cooling system was undersized for "
        "the venue's HVAC limitations. Zeltron subsequently redesigned the cooling system "
        "with a 2C safety margin (effective operating range: 20.4C to 24.4C). No data was "
        "lost. The NATO contract was signed 6 weeks later after a successful repeat demo.\n\n"
        "Future Roadmap:\n"
        "  - QA-8 (planned Q3 2025): 1,200 teraflops target, quad-layer spiral, 16,000+ "
        "resonators. Focus on power efficiency (target: <3.5 kW peak).\n"
        "  - QA-9 (planned 2026): 2,000+ teraflops target. Exploring hybrid barium "
        "titanate / lithium tantalate resonator arrays (Project Crescendo output). First "
        "processor targeting general-purpose quantum-acoustic workloads beyond cryptanalysis."
    )
    pdf.multi_cell(0, 5, text)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    pdf.output(OUTPUT)
    print(f"PDF written to {OUTPUT} ({pdf.pages_count} pages)")


if __name__ == "__main__":
    build_pdf()
