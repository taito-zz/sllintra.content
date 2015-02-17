This package provides behaviors and vocabularies for dexterity content type.

Bahavior
--------

* sllintra.content.interfaces.IBasic

This moves required title to unrequisite title.

* sllintra.content.interfaces.INameFromTitleOrFileName

This takes first file or title as id. So if you have multiple file, you need to be careful with the order of the file field.


Vocabulary
----------

Vocabularies are constructed from dexterity *Choice* and ̈́*Multiple Choice* Field.
The name of vocabulary is from dexterity content type name and field name like:: content_type_name - field_name.
