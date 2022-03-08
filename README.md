# WikiTool

**Requires pandoc and aspell installed for user**

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
