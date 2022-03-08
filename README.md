# WikiTool

**Requires [pandoc](https://pandoc.org/installing.html) and [aspell](http://aspell.net/)[^1] installed for user**

**Requires python library [anytree](https://anytree.readthedocs.io/en/latest/installation.html) installed**

## TODO

* [ ] Creata a config file with the following fields 
  * absolute path for root
  * absolute path for css files
  * absolute path for html files
  * absolute path for resource folder (creates assets folder in out if not specified)
  * [ ] add code compatibility with this config file
* [ ] implement .css, .tmpl, and .js for different types
  * standard (default; already done)
  * maker's notes
  * two-column
  * more added if needed
* [ ] Spell-check
  * lua script now identifies which words are zean and english by checking if they are surrounded by {{...}}
  * Next is to add zean dictionary to aspell
    * Figure out how to use aspell
  
 [^1]: Windows Port 0.5 works
