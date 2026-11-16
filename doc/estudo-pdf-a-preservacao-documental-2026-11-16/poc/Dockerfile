FROM mirror.gcr.io/library/python:3.13-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ghostscript qpdf poppler-utils fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pikepdf==9.* pyhanko==0.29.* pyhanko-certvalidator img2pdf pillow reportlab
