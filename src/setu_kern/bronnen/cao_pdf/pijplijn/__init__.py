"""KOPIE van cao_setu_v2/llm_pipeline: een CAO-pdf inlezen (marker-pdf), indelen in artikelen/leden, embedden en
zoeken (FAISS). Alleen de imports zijn aangepast.

Afwijking van het origineel: dit bestand importeert ``cli`` niet meer, zodat ``pijplijn.store`` e.d. te gebruiken
zijn zonder marker-pdf te laden. De CLI draai je met ``python -m setu_kern.bronnen.cao_pdf.pijplijn.cli``.
"""
