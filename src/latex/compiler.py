"""
Phase 5 LaTeX PDF Compiler.
Wraps pdflatex command-line tool via subprocess.
Verifies layout metrics:
  - Scans compilation stdout and log files for 'Overfull \\hbox' warnings.
  - Parses compiled PDF via pypdf to verify exact 1-page document length.
"""

import os
import re
import subprocess
from typing import Dict, Any, Optional
from pypdf import PdfReader


class LaTeXCompiler:
    def __init__(self):
        pass

    def compile_pdf(self, tex_path: str, output_dir: str = "./output") -> Dict[str, Any]:
        """
        Compiles a .tex file to .pdf using pdflatex.
        Verifies 1-page count and scans for Overfull \\hbox warnings.
        """
        if not os.path.exists(tex_path):
            raise FileNotFoundError(f"LaTeX file not found at {tex_path}")

        os.makedirs(output_dir, exist_ok=True)
        tex_abs = os.path.abspath(tex_path)
        out_abs = os.path.abspath(output_dir)

        # Check if pdflatex is available on PATH
        try:
            subprocess.run(["pdflatex", "--version"], capture_output=True, check=True)
            pdflatex_available = True
        except Exception:
            pdflatex_available = False

        if not pdflatex_available:
            # Fallback: check if docker is available to run texlive container
            try:
                subprocess.run(["docker", "run", "--rm", "texlive/texlive", "pdflatex", "--version"], capture_output=True, check=True)
                docker_latex_available = True
            except Exception:
                docker_latex_available = False

            if not docker_latex_available:
                pdf_filename = os.path.basename(tex_path).replace(".tex", ".pdf")
                pdf_expected_path = os.path.join(output_dir, pdf_filename)
                return {
                    "success": False,
                    "compiled": False,
                    "pdf_path": pdf_expected_path,
                    "overfull_warnings": [],
                    "page_count": 0,
                    "is_one_page": True,
                    "warning": f"pdflatex is not installed on system PATH. Tex file generated at {tex_path}."
                }

        # Run pdflatex twice for reference resolution
        cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={out_abs}", tex_abs]

        stdout_text = ""
        stderr_text = ""

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=out_abs)
            stdout_text = proc.stdout
            stderr_text = proc.stderr

            # Second pass for hyperref
            subprocess.run(cmd, capture_output=True, text=True, cwd=out_abs)
        except Exception as e:
            return {
                "success": False,
                "compiled": False,
                "pdf_path": None,
                "overfull_warnings": [],
                "page_count": 0,
                "is_one_page": False,
                "warning": f"pdflatex execution error: {str(e)}"
            }

        pdf_filename = os.path.basename(tex_path).replace(".tex", ".pdf")
        pdf_path = os.path.join(output_dir, pdf_filename)

        # ----------------------------------------------------
        # 1. Overfull \hbox Warning Detection
        # ----------------------------------------------------
        overfull_matches = re.findall(r'Overfull \\hbox \([^\)]+\)', stdout_text)
        log_path = tex_path.replace(".tex", ".log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                log_content = lf.read()
                overfull_matches.extend(re.findall(r'Overfull \\hbox \([^\)]+\)', log_content))

        # ----------------------------------------------------
        # 2. Page Count Verification via PyPDF
        # ----------------------------------------------------
        page_count = 0
        is_one_page = True
        warnings_list = list(set(overfull_matches))

        if os.path.exists(pdf_path):
            try:
                reader = PdfReader(pdf_path)
                page_count = len(reader.pages)
                is_one_page = (page_count == 1)
                if not is_one_page:
                    warnings_list.append(f"LAYOUT OVERFLOW: PDF output is {page_count} pages (expected exactly 1 page).")
            except Exception as e:
                warnings_list.append(f"Could not read PDF page count: {str(e)}")

        return {
            "success": os.path.exists(pdf_path) and is_one_page,
            "compiled": os.path.exists(pdf_path),
            "pdf_path": pdf_path if os.path.exists(pdf_path) else None,
            "overfull_warnings": warnings_list,
            "page_count": page_count,
            "is_one_page": is_one_page,
            "warning": warnings_list[0] if warnings_list else None
        }
