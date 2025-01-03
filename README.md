# fp-convert

It converts a freeplane mindmap to print-quality PDF. At present it converts a mindmap to a project specification document. The same template can be used to build a knowledgebase and print it out as a beautiful PDF document. It uses LaTeX document as its intermediate format before doing the final conversion into PDF.

Following image summarizes what fp-convert can do if it is provided with a suitably prepared freeplane mindmap.
![fp-convert [options] mindmap-file pdf-file](docs/examples/blooper-specs/images/fp-convert-summary-image.png)

# license

This application is released under Apache License (v2). You are free to use it in commercial as well as in open source projects, based on the pertient licencing terms.

# features

fp-convert is a commanline tool written in Python which uses fp_convert module to carry out its work. The same module can be invoked from other Python programs too, to generate required PDF documents. At present it is designed to generate project specification document for any software or IT based projects. We would be adding support for other kinds of documents in future, based on the demand from the community. At the same time it should not be presumed that the generated document would not be useful for capturing other knowledge-items. The LaTeX base documentclass used in `article'. Hence you can use fp-convert to generate any kind of document, as long as you follow certain conventions while creating your mindmap.

## print-quality PDF generation

fp-convert can generate PDF file using TeX/LaTeX text processing system. It creates beautiful, and compact documents which follow almost all typographic conventions followed in a standard TeX based document template.

## separation of document's data and meta-data

The document's content is kept separate from the standard meta-data like page-geometry, logo-images and their dimentions, colours of various artifacts etc. Following is the meta-ino stored in the root node of the sample mindmap.

---

```
Title: Project Specifications of Blooper App
Version: 1.2
Date: 15 November, 2024
Author: Whoopie Bard $<$whoopie@clueless.dev$>$\\Changu Bhai $<$changu.bhai@clueless.dev$>$
Client: Blooper Corporation Inc.
Vendor: Clueless Developers' Consortium
TP_Top_Logo: images/blooper_logo.pdf
TP_Bottom_Logo: images/clueless_devs_consortium.pdf
C_Header_Text: Project Specifications of Blooper App
R_Header_Text: Non-Confidential
L_Header_Logo: images/blooper_logo.pdf
C_Footer_Logo: images/clueless_devs_consortium.pdf
R_Footer_Text: \small{Page \thepage\- of \pageref*{LastPage}}
Header_Thickness: 0.4
Footer_Thickness: 0.4
```

---

There are additional controls too are possible, which are not readily available here. For example, by creating your own Theme, Color, Config classes, you can control the resultant document in much more fine grained manner. At present, the documentation is quite sparese. But we hope to improve it over some time.

## sections, subsections, and more

Except root node, all following nodes in a mindmap are treated as sections, their subsections, their subsubsections and more. You can attain maximum depth of 5 in this manner. The node's text is treated as header of respective sections, and the note-text in each of them are rendered as section-content. Every linke-break in the note-text is taken as the start of a new paragraph in respective section.

## unordered lists

If a node is to be treated in a different way, it should be annotated with a suitable icon.
