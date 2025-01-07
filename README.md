# fp-convert

It converts a freeplane mindmap to print-quality PDF. At present it converts a mindmap to a project specification document. The same template can be used to build a knowledgebase and print it out as a beautiful PDF document. It uses LaTeX document as its intermediate format before doing the final conversion into PDF.

Following image summarizes what fp-convert can do if it is provided with a suitably prepared freeplane mindmap.
![fp-convert [options] mindmap-file pdf-file](docs/examples/blooper-specs/images/fp-convert-summary-image.png)

# license

This application is released under Apache(v2) License. You are free to use its code in commercial as well as in open source projects, under pertient licencing terms. But please note that one of the components used in this project ([freeplane-python-io](https://github.com/nnako/freeplane-python-io)) is released under GPLv3. This may affect your chances of using this tool along with non-GPLed code - like in a proprietary tool. But if you are using this tool as a standalone application executed via command line, then probably you are allowed to use it in your commercial products too. But it would be better to consult a lawyer familiar with IP and software licenses before opting for that approach.

# software used

fp-convert is standing on the shoulders of giants like Python and TeX/LaTeX which doesn't need any introductions. But two critical components without which this endeavour would not have been possibe are [PyLaTeX](https://github.com/JelteF/PyLaTeX) and [freeplane-python-io](https://github.com/nnako/freeplane-python-io) (thanks nnako for all those timely help :).

# features

fp-convert is a commanline tool written in Python which uses fp_convert module to carry out its work. The same module can be invoked from other Python programs too, to generate required PDF documents. At present it is designed to generate project specification document for any software or IT based projects. We would be adding support for other kinds of documents in future, based on the demand from the community. At the same time it should not be presumed that the generated document would not be useful for capturing other knowledge-items. fp-convert uses LaTeX base document class `article'. Hence you can use fp-convert to generate any kind of document which can be built using that document class, as long as you follow certain conventions while creating your mindmap.

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

Except root node, all following nodes in a mindmap are treated as sections, their subsections, their subsubsections and more. You can attain maximum depth of 5 in this manner. The node's text is treated as header of respective sections, and the note-text in each of them are rendered as section-content. Every linke-break in the note-text is taken as the start of a new paragraph in respective section. If a node is to be treated in a different way, it should be annotated with a suitable icon.

## unordered lists

If a node is annotated with list icon (![list icon](docs/examples/blooper-specs/images/list.png)), a nested bullet-list (generated by LaTeX's \itemize) is created using its children and their respective children. The depth of list can be up to 3.

## ordered lists

If a node is annotated with list icon (![list icon](docs/examples/blooper-specs/images/list.png)) as well as input numbers icon (![input numbers icon](docs/examples/blooper-specs/images/numbers.png)), then the list created from the contents of the direct children of that node would be an ordered list. The depth of the list is not dependent on the type of the list. Overall the total depth can not be more than 3, irrespective of whichever types of lists are mixed and matched. Also annotating a node without list icon but with input numbers icon would not generate an oredered list unless at least one of the parent-node between that node and the root node is annotated with the list icon. It means, starting an ordered list with a node annotated only with the input numbers icon would not be possible. Please refer the sample mindmap provided with fp-convert how such lists work.

## tabular views

By annotating any node with generic icon (![generic icon](docs/examples/blooper-specs/images/table.png)), a tabular view can be built. The first level of children after that node would be rendered as first column of respective rows in that table. The second level onwards the nodes would contain the column header and content for second column onwards. Each such row should contain the text in X:Y format, where X would be the column header, and Y would be the column-value. Check the sample mindmap and the resultant PDF file to know how the contents are placed and rendered.

## verbatim/code/json/html/xml views

By annotating any node with JSON icon (![json icon](docs/examples/blooper-specs/images/json.png)), a verbatim block can be created from its content using LaTeX's verbatim environment. Please note that the whole node's content would be rendered in verbatim mode. This kind of rendering is suitable to display HTML, XML, JSON, as well as software code.

## images

If an image is to be rendered in a particular section or subsection, then node corresponding to that section should be annotated with image icon (![image icon](docs/examples/blooper-specs/images/image.png)). The raster image formats like JPEG and PNG are supported. If you want to use vector graphics, then attach SVG based images. They would be auto-converted to PDF and used in the resultant PDF document.

## warnings

If some kind of warning-text in red is to be rendered, then that node should be annotated with stop icon (![stop icon](docs/examples/blooper-specs/images/stop.png)), and the warning-text should be placed as a note in that node. Then this text would be rendered in a red box for easy identification.

## marked for removal

If any block of text elements rendered using a node is to be marked for removal in future, then annotate that node with cross icon (![cross icon](docs/examples/blooper-specs/images/cross.png)). Then the content of this and its children would be distinctly marked for removal using red text and lines.

## marked as new

If some text is to be flagged as new, then annotate respective nodes using plus icon (![plus icon](docs/examples/blooper-specs/images/plus.png)). Such blocks of text would be marked as New for easy identification.

# additional text

Besides rendering the contents of nodes, addtional text can be included as note-text in each node. Depending on the way the node is annotated (or not), those note-texts would be rendered too in the resultant PDF file.

# future plans

This code can reasonably be extended to include additional document types. For example it would be possible to come up with a schema for composing music using freeplane, and it could be rendered as sheet music using MusiXTeX. Similarly using CircuiTikz, one can come up with a scheme to build and render electronic circuit too. Similar possibilities are endless. If one can design a convention to build a mindmap and define a template to render its content using TeX/LaTeX, a class equivalent to psdoc.py can be integrated and included as part of fp-convert.
