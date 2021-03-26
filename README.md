URL: https://repl.it/@mrjsng/CapstoneProject

# [NYJC] JC2 Capstone project: Bus search

The purpose of this project is to develop an application that allows users to search for bus data.

In this project, you will demonstrate the knowledge and skills you have picked up so far in your H2 Computing lessons.

Your project must:
1. Use an **SQL database** to store data
2. Use Flask to serve a web app that allows user interaction
3. Provide a feature that involves both database lookup **and** data processing; it cannot only be a browsing/lookup application
   - e.g. Searching for nearest bus stop to a point
   - e.g. Searching for common bus stops between two routes
   - e.g. Determining travel time between two points on a bus route
   - e.g. Calculating travel fare between two points on a bus route
   - e.g. For two given bus stops, search for all routes that pass through both bus stops

The data for bus routes, bus services, and bus stops comes from the [LTA Data Mall API](https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html). You can refer to the [API User Guide](https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf) (Sections 2.2 to 2.4) for more details and documentation on the data format.

# Grading criteria

**Syntax**
- documentation **[0-3]**
  Docstrings for most nonstandard methods are present
- adherence to conventions **[0-3]**
  Appropriate use of whitespace and indentation for human readability
- organisation of code (abstraction) **[0-3]**
  Code is logically organised, and split into modules to enhance ease of understanding

**Object-Oriented Programming**
- appropriate use of encapsulation **[0-3]**
  Data required by the application is appropriately broken up into classes/objects
- appropriate use of inheritance **[0-3]**
  Classes with a common purpose inherit from a base class
- appropriate use of polymorphism **[0-3]**
  Classes that are used in the same way implement polymorphic methods

**Algorithms and Data Structures**
- use of sorting/searching algorithms/data structures **[0-3]**
  Appropriate use of sorting/searching algorithms where required
  (Use of built-in Python sort, which actually uses the Timsort algorithm, is allowed, but no marks will be awarded)
- performance of implementation **[0-3]**
  Algorithm is implemented with performance close to reference (i.e. code is efficient)

**Design**
- Use of data modelling techniques for app structuring **[0-3]**
  UML diagram provided showing organisation of classes
  Code implementation follows UML diagram
- use of ER modelling techniques for data **[0-3]**
  ER diagram provided showing database schema (SQL)
  Database implementation follows ER diagram
- Usability **[0-3]**
  App interface (web) follows usability principles

**Web Programming**
- use of appropriate HTTP methods and HTML forms **[0-3]**
  Appropriate use of GET & POST methods, and HTML form elements
  (Up to bonus [1] given for use of appropriate HTML form elements)
- HTML, formatting, and CSS **[0-3]**
  Appropriate use of HTML elements for organisation, and CSS classes for formatting

**Databases**
- data validation and verification **[0-3]**
  Data validation is carried out appropriately on user input before being used
  Data retrieved should be verified where appropriate, e.g. to avoid returning an error to the user.
- data security **[0-3]**
  Secure data practices are used
