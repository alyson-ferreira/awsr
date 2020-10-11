====
awsr
====

-----------
Description
-----------

AWS Rotate - Rotate Access Key

-----
Usage
-----

    awsr -h

--------
Examples
--------

    # Rotate user johndoe access key quietly in profile default
    awsr johndoe

    # Rotate user marie access key quietly in profile marie
    awsr marie -p marie

    # Rotate, then show old and new key ids
    awsr cooluser -v
