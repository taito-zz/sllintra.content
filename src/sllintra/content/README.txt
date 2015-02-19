This package provides behaviors and vocabularies for dexterity content type.

Bahavior
--------

* ``sllintra.content.interfaces.IBasic``

This moves required title to unrequisite title.

* ``sllintra.content.interfaces.INameFromTitleOrFileName``

This takes first file or title as id. So if you have multiple file, you need to be careful with the order of the file field.

Vocabulary
----------

Vocabularies are constructed from dexterity **Choice** and/or **Multiple Choice** Field.
The name of vocabulary is from dexterity content type name and field name like **content_type_name - field_name**.

How to create Archive content type
----------------------------------

1. Add New Dexterity Content Type with short name : ``archive``.

2. Disable behaviors: **Dublin Core metadata** and **Name from title**.

3. Enabale behaviors: **Basic metadata with unrequisite title** and **Name from title or file name**.

4. Add file field with whatever name.

To make multiple choice field radio button
------------------------------------------

1. Add multiple choice field.

2. Go to the field setting.

3. There is field type select field. Choose radio button field from there.

When you want to use the same vocabularies you have set in multiple choice field or choice field
-------------------------------------------------------------------------------------------------

1. Add multiple choice field or choice field.

2. Go to the field setting.

3. In the vocabulary name, you see **content_type_name - field_name**, so select appropriate one for your need.

* You may find the same vocabularies in eea.facetednavigation.
