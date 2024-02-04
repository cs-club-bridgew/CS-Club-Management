"""Provides a class for generating a docket report using LaTeX."""


import os
import subprocess
import tempfile
from datetime import datetime
from time import time

def clear_dockets():
    """Clears the docket directory."""
    print("Clearing dockets...")
    subprocess.run(["rm", "/home/www/Invoices/reports/*"])
    subprocess.run(["mkdir", "-p", "/home/www/Invoices/reports/"])

def generate_docket_report(docket: list, start_date: str, end_date: str, user_name: str):
    """Generates a docket report using LaTeX.

    Args:
        docket (list): A list of dictionaries containing docket items.
        start_date (str): The start date of the report.
        end_date (str): The end date of the report.
        user_name (str): The name of the user generating the report.

    Returns:
        str: The path to the generated PDF.
    """
    
    #clear_dockets()
    template_header = r"""
\documentclass[twoside]{article}
\usepackage[margin=3cm]{geometry}
\usepackage{fancyhdr}

\def\docAuthor{""" + user_name + r"""}

% Header
\pagestyle{fancy}
\fancyhead[LE,RO]{Generated \today}
\fancyhead[RE, LO]{\docAuthor}

\begin{document}
\begin{center}
    \huge{Docket Report}\\
    \large{Generated \today}
    \large{From """ + start_date + r""" to """ + end_date + r"""}
\end{center}
\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\textbf{ID} & \textbf{Date} & \textbf{Created By}  & \textbf{F} & \textbf{O} & \textbf{A} & \textbf{Status} \\
\hline
"""
    for idx, item in enumerate(docket):
        template_header += f"{item['docket_id']} & {item['create_date']} & {item['created_by']} & {item.get('in_favor', 0)} & {item.get('opposed', 0)} & {item.get('abstained', '0')} & {item['status']} \\\\"
        if (idx + 2) % 49 == 0:
            template_header += r"""\hline
\end{tabular}
\newpage
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\textbf{ID} & \textbf{Date} & \textbf{Created By}  & \textbf{F} & \textbf{O} & \textbf{A} & \textbf{Status} \\
\hline
"""
    template_footer = r"""
\hline
\end{tabular}
\end{center}
\end{document}
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "docket_report.tex"), "w") as f:
            f.write(template_header)
            f.write(template_footer)
        subprocess.run(["/usr/bin/pdflatex", "-output-directory", temp_dir, os.path.join(temp_dir, "docket_report.tex")])
        file_path = f"./reports/docket_report_{int(time())}.pdf"
        subprocess.run(["/usr/bin/mv", os.path.join(temp_dir, "docket_report.pdf"), file_path])
        return file_path
