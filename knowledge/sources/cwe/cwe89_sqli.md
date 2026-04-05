xml version="1.0" encoding="iso-8859-1"?

CWE -
CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') (4.19.1)

# Common Weakness Enumeration

A community-developed list of SW & HW weaknesses that can become vulnerabilities

|  |  |
| --- | --- |
| Home > CWE List > CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') (4.19.1) |  |

---

- Home
- Who We Are
  User Stories
  History
  Documents
  Videos
- Basics

  Root Cause Mapping   ►

  Guidance
  Quick Tips
  Examples

  How to Contribute Weakness Content
  FAQs
  Glossary
- Top-N Lists   ►

  Top 25 Software
  Top Hardware
  Top 10 KEV Weaknesses

  CWE List   ►

  Current Version
  Reports
  Visualizations
  Releases Archive

  Downloads
  REST API
- News   ►

  Current News
  Blog
  Podcast
  News Archive

  CWE Board
  Working Groups & Special Interest Groups
  Email Lists
- Search CWE List
  Search Website

|  |  |  |
| --- | --- | --- |
|  |  |  |
| |  |  | | --- | --- | | CWE Glossary Definition |  | |  | |        CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')  |  | | --- | | Weakness ID: 89   Vulnerability Mapping: ALLOWED This CWE ID may be used to map to real-world vulnerabilities   Abstraction: Base Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. |  View customized information:  For users who are interested in more notional aspects of a weakness. Example: educators, technical writers, and project/program managers.  For users who are concerned with the practical application and details about the nature of a weakness and how to prevent it from happening. Example: tool developers, security researchers, pen-testers, incident response analysts.  For users who are mapping an issue to CWE/CAPEC IDs, i.e., finding the most appropriate CWE for a specific issue (e.g., a CVE record). Example: tool developers, security researchers.  For users who wish to see all available information for the CWE/CAPEC entry.  For users who want to customize what details are displayed.  ×  Edit Custom Filter  Description  |  |  | | --- | --- | | The product constructs all or part of an SQL command using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended SQL command when it is sent to a downstream component. Without sufficient removal or quoting of SQL syntax in user-controllable inputs, the generated SQL query can cause those inputs to be interpreted as SQL instead of ordinary user data. |  |  Alternate Terms  |  |  | | --- | --- | | SQL injection | a common attack-oriented phrase | | SQLi | a common abbreviation for "SQL injection" |  Common Consequences  This table specifies different individual consequences associated with the weakness. The Scope identifies the application security area that is violated, while the Impact describes the negative technical impact that arises if an adversary succeeds in exploiting this weakness. The Likelihood provides information about how likely the specific consequence is expected to be seen relative to the other consequences in the list. For example, there may be high likelihood that a weakness will be exploited to achieve a certain impact, but a low likelihood that it will be exploited to achieve a different impact.  | Impact | Details | | --- | --- | | *Execute Unauthorized Code or Commands* | Scope: Confidentiality, Integrity, Availability   Adversaries could execute system commands, typically by changing the SQL statement to redirect output to a file that can then be executed. | | *Read Application Data* | Scope: Confidentiality   Since SQL databases generally hold sensitive data, loss of confidentiality is a frequent problem with SQL injection vulnerabilities. | | *Gain Privileges or Assume Identity; Bypass Protection Mechanism* | Scope: Authentication   If poor SQL commands are used to check user names and passwords or perform other kinds of authentication, it may be possible to connect to the product as another user with no previous knowledge of the password. | | *Bypass Protection Mechanism* | Scope: Access Control   If authorization information is held in a SQL database, it may be possible to change this information through the successful exploitation of a SQL injection vulnerability. | | *Modify Application Data* | Scope: Integrity   Just as it may be possible to read sensitive information, it is also possible to modify or even delete this information with a SQL injection attack. |  Potential Mitigations  | Phase(s) | Mitigation | | --- | --- | | Architecture and Design | Strategy: *Libraries or Frameworks*  Use a vetted library or framework that does not allow this weakness to occur or provides constructs that make this weakness easier to avoid [REF-1482].  For example, consider using persistence layers such as Hibernate or Enterprise Java Beans, which can provide significant protection against SQL injection if used properly. | | Architecture and Design | Strategy: *Parameterization*  If available, use structured mechanisms that automatically enforce the separation between data and code. These mechanisms may be able to provide the relevant quoting, encoding, and validation automatically, instead of relying on the developer to provide this capability at every point where output is generated.  Process SQL queries using prepared statements, parameterized queries, or stored procedures. These features should accept parameters or variables and support strong typing. Do not dynamically construct and execute query strings within these features using "exec" or similar functionality, since this may re-introduce the possibility of SQL injection. [REF-867] | | Architecture and Design; Operation | Strategy: *Environment Hardening*  Run your code using the lowest privileges that are required to accomplish the necessary tasks [REF-76]. If possible, create isolated accounts with limited privileges that are only used for a single task. That way, a successful attack will not immediately give the attacker access to the rest of the software or its environment. For example, database applications rarely need to run as the database administrator, especially in day-to-day operations.  Specifically, follow the principle of least privilege when creating user accounts to a SQL database. The database users should only have the minimum privileges necessary to use their account. If the requirements of the system indicate that a user can read and modify their own data, then limit their privileges so they cannot read/write others' data. Use the strictest permissions possible on all database objects, such as execute-only for stored procedures. | | Architecture and Design | For any security checks that are performed on the client side, ensure that these checks are duplicated on the server side, in order to avoid CWE-602. Attackers can bypass the client-side checks by modifying values after the checks have been performed, or by changing the client to remove the client-side checks entirely. Then, these modified values would be submitted to the server. | | Implementation | Strategy: *Output Encoding*  While it is risky to use dynamically-generated query strings, code, or commands that mix control and data together, sometimes it may be unavoidable. Properly quote arguments and escape any special characters within those arguments. The most conservative approach is to escape or filter all characters that do not pass an extremely strict allowlist (such as everything that is not alphanumeric or white space). If some special characters are still needed, such as white space, wrap each argument in quotes after the escaping/filtering step. Be careful of argument injection (CWE-88).  Instead of building a new implementation, such features may be available in the database or programming language. For example, the Oracle DBMS\_ASSERT package can check or enforce that parameters have certain properties that make them less vulnerable to SQL injection. For MySQL, the mysql\_real\_escape\_string() API function is available in both C and PHP. | | Implementation | Strategy: *Input Validation*  Assume all input is malicious. Use an "accept known good" input validation strategy, i.e., use a list of acceptable inputs that strictly conform to specifications. Reject any input that does not strictly conform to specifications, or transform it into something that does.  When performing input validation, consider all potentially relevant properties, including length, type of input, the full range of acceptable values, missing or extra inputs, syntax, consistency across related fields, and conformance to business rules. As an example of business rule logic, "boat" may be syntactically valid because it only contains alphanumeric characters, but it is not valid if the input is only expected to contain colors such as "red" or "blue."  Do not rely exclusively on looking for malicious or malformed inputs. This is likely to miss at least one undesirable input, especially if the code's environment changes. This can give attackers enough room to bypass the intended validation. However, denylists can be useful for detecting potential attacks or determining which inputs are so malformed that they should be rejected outright.  When constructing SQL query strings, use stringent allowlists that limit the character set based on the expected value of the parameter in the request. This will indirectly limit the scope of an attack, but this technique is less important than proper output encoding and escaping.  Note that proper output encoding, escaping, and quoting is the most effective solution for preventing SQL injection, although input validation may provide some defense-in-depth. This is because it effectively limits what will appear in output. Input validation will not always prevent SQL injection, especially if you are required to support free-form text fields that could contain arbitrary characters. For example, the name "O'Reilly" would likely pass the validation step, since it is a common last name in the English language. However, it cannot be directly inserted into the database because it contains the "'" apostrophe character, which would need to be escaped or otherwise handled. In this case, stripping the apostrophe might reduce the risk of SQL injection, but it would produce incorrect behavior because the wrong name would be recorded.  When feasible, it may be safest to disallow meta-characters entirely, instead of escaping them. This will provide some defense in depth. After the data is entered into the database, later processes may neglect to escape meta-characters before use, and you may not have control over those processes. | | Architecture and Design | Strategy: *Enforcement by Conversion*  When the set of acceptable objects, such as filenames or URLs, is limited or known, create a mapping from a set of fixed input values (such as numeric IDs) to the actual filenames or URLs, and reject all other inputs. | | Implementation | Ensure that error messages only contain minimal details that are useful to the intended audience and no one else. The messages need to strike the balance between being too cryptic (which can confuse users) or being too detailed (which may reveal more than intended). The messages should not reveal the methods that were used to determine the error. Attackers can use detailed information to refine or optimize their original attack, thereby increasing their chances of success.  If errors must be captured in some detail, record them in log messages, but consider what could occur if the log messages can be viewed by attackers. Highly sensitive information such as passwords should never be saved to log files.  Avoid inconsistent messaging that might accidentally tip off an attacker about internal state, such as whether a user account exists or not.  In the context of SQL Injection, error messages revealing the structure of a SQL query can help attackers tailor successful attack strings. | | Operation | Strategy: *Firewall*  Use an application firewall that can detect attacks against this weakness. It can be beneficial in cases in which the code cannot be fixed (because it is controlled by a third party), as an emergency prevention measure while more comprehensive software assurance measures are applied, or to provide defense in depth [REF-1481.  Effectiveness: Moderate  **Note:**  An application firewall might not cover all possible input vectors. In addition, attack techniques might be available to bypass the protection mechanism, such as using malformed inputs that can still be processed by the component that receives those inputs. Depending on functionality, an application firewall might inadvertently reject or modify legitimate requests. Finally, some manual effort may be required for customization. | | Operation; Implementation | Strategy: *Environment Hardening*  When using PHP, configure the application so that it does not use register\_globals. During implementation, develop the application so that it does not rely on this feature, but be wary of implementing a register\_globals emulation that is subject to weaknesses such as CWE-95, CWE-621, and similar issues. |  Relationships  This table shows the weaknesses and high level categories that are related to this weakness. These relationships are defined as ChildOf, ParentOf, MemberOf and give insight to similar items that may exist at higher and lower levels of abstraction. In addition, relationships such as PeerOf and CanAlsoBe are defined to show similar weaknesses that the user may want to explore.  Relevant to the view "Research Concepts" (View-1000) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 943 | Improper Neutralization of Special Elements in Data Query Logic | | ParentOf | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 564 | SQL Injection: Hibernate | | CanFollow | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 456 | Missing Initialization of a Variable |  Relevant to the view "Software Development" (View-699) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 137 | Data Neutralization Issues |  Relevant to the view "Weaknesses for Simplified Mapping of Published Vulnerabilities" (View-1003) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 74 | Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection') |  Relevant to the view "Architectural Concepts" (View-1008) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1019 | Validate Inputs |  Relevant to the view "CISQ Quality Measures (2020)" (View-1305) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ParentOf | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 564 | SQL Injection: Hibernate |  Relevant to the view "Weaknesses in OWASP Top Ten (2013)" (View-928) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ParentOf | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 564 | SQL Injection: Hibernate |  Modes Of Introduction  The different Modes of Introduction provide information about how and when this weakness may be introduced. The Phase identifies a point in the life cycle at which introduction may occur, while the Note provides a typical scenario related to introduction during the given phase.  | Phase | Note | | --- | --- | | Implementation | REALIZATION: This weakness is caused during implementation of an architectural security tactic. | | Implementation | This weakness typically appears in data-rich applications that save user inputs in a database. |  Applicable Platforms  This listing shows possible areas for which the given weakness could appear. These may be for specific named Languages, Operating Systems, Architectures, Paradigms, Technologies, or a class of such platforms. The platform is listed along with how frequently the given weakness appears for that instance.  |  |  | | --- | --- | | Languages | Class: Not Language-Specific (Undetermined Prevalence)  SQL (Often Prevalent) | | Technologies | Database Server (Undetermined Prevalence) |  Likelihood Of Exploit  High  Demonstrative Examples  Example 1  Selected Observed Examples  *Note: this is a curated list of examples for users to understand the variety of ways in which this weakness can be introduced. It is not a complete list of all CVEs that are related to this CWE entry.*  | Reference | Description | | --- | --- | | CVE-2024-6847 | SQL injection in AI chatbot via a conversation message | | CVE-2025-26794 | SQL injection in e-mail agent through SQLite integration | | CVE-2023-32530 | SQL injection in security product dashboard using crafted certificate fields | | CVE-2021-42258 | SQL injection in time and billing software, as exploited in the wild per CISA KEV. | | CVE-2021-27101 | SQL injection in file-transfer system via a crafted Host header, as exploited in the wild per CISA KEV. | | CVE-2020-12271 | SQL injection in firewall product's admin interface or user portal, as exploited in the wild per CISA KEV. | | CVE-2019-3792 | An automation system written in Go contains an API that is vulnerable to SQL injection allowing the attacker to read privileged data. | | CVE-2004-0366 | chain: SQL injection in library intended for database authentication allows SQL injection and authentication bypass. | | CVE-2008-2790 | SQL injection through an ID that was supposed to be numeric. | | CVE-2008-2223 | SQL injection through an ID that was supposed to be numeric. | | CVE-2007-6602 | SQL injection via user name. | | CVE-2008-5817 | SQL injection via user name or password fields. | | CVE-2003-0377 | SQL injection in security product, using a crafted group name. | | CVE-2008-2380 | SQL injection in authentication library. | | CVE-2017-11508 | SQL injection in vulnerability management and reporting tool, using a crafted password. |  Weakness Ordinalities  | Ordinality | Description | | --- | --- | | Primary | (where the weakness exists independent of other weaknesses) |  Resultant | (where the weakness is typically related to the presence of some other weaknesses) | |

Detection
Methods

| Method | Details |
| --- | --- |
| Automated Static Analysis | This weakness can often be detected using automated static analysis tools. Many modern tools use data flow analysis or constraint-based techniques to minimize the number of false positives.  Automated static analysis might not be able to recognize when proper input validation is being performed, leading to false positives - i.e., warnings that do not have any security consequences or do not require any code changes.  Automated static analysis might not be able to detect the usage of custom API functions or third-party libraries that indirectly invoke SQL commands, leading to false negatives - especially if the API/library code is not available for analysis. **Note:**This is not a perfect solution, since 100% accuracy and coverage are not feasible. |
| Automated Dynamic Analysis | This weakness can be detected using dynamic tools and techniques that interact with the software using large test suites with many diverse inputs, such as fuzz testing (fuzzing), robustness testing, and fault injection. The software's operation may slow down, but it should not become unstable, crash, or generate incorrect results.  Effectiveness: Moderate |
| Manual Analysis | Manual analysis can be useful for finding this weakness, but it might not achieve desired code coverage within limited time constraints. This becomes difficult for weaknesses that must be considered for all inputs, since the attack surface can be too large. |
| Automated Static Analysis - Binary or Bytecode | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Bytecode Weakness Analysis - including disassembler + source code weakness analysis - Binary Weakness Analysis - including disassembler + source code weakness analysis  Effectiveness: High |
| Dynamic Analysis with Automated Results Interpretation | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Database Scanners   Cost effective for partial coverage:   - Web Application Scanner - Web Services Scanner  Effectiveness: High |
| Dynamic Analysis with Manual Results Interpretation | According to SOAR [REF-1479], the following detection techniques may be useful:  Cost effective for partial coverage:   - Fuzz Tester - Framework-based Fuzzer  Effectiveness: SOAR Partial |
| Manual Static Analysis - Source Code | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Manual Source Code Review (not inspections)   Cost effective for partial coverage:   - Focused Manual Spotcheck - Focused manual analysis of source  Effectiveness: High |
| Automated Static Analysis - Source Code | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Source code Weakness Analyzer - Context-configured Source Code Weakness Analyzer  Effectiveness: High |
| Architecture or Design Review | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Formal Methods / Correct-By-Construction   Cost effective for partial coverage:   - Inspection (IEEE 1028 standard) (can apply to requirements, design, source code, etc.)  Effectiveness: High |

Memberships

This MemberOf Relationships table shows additional CWE Categories and Views that
reference this weakness as a member. This information is often useful in understanding where a
weakness fits within the context of external information sources.

| Nature | Type | ID | Name |
| --- | --- | --- | --- |
|  |  |  |  |
| --- | --- | --- | --- |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 635 | Weaknesses Originally Used by NVD from 2008 to 2016 |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 713 | OWASP Top Ten 2007 Category A2 - Injection Flaws |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 722 | OWASP Top Ten 2004 Category A1 - Unvalidated Input |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 727 | OWASP Top Ten 2004 Category A6 - Injection Flaws |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 751 | 2009 Top 25 - Insecure Interaction Between Components |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 801 | 2010 Top 25 - Insecure Interaction Between Components |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 810 | OWASP Top Ten 2010 Category A1 - Injection |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 864 | 2011 Top 25 - Insecure Interaction Between Components |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 884 | CWE Cross-section |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 929 | OWASP Top Ten 2013 Category A1 - Injection |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 990 | SFP Secondary Cluster: Tainted Input to Command |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1005 | 7PK - Input Validation and Representation |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1027 | OWASP Top Ten 2017 Category A1 - Injection |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1131 | CISQ Quality Measures (2016) - Security |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1200 | Weaknesses in the 2019 CWE Top 25 Most Dangerous Software Errors |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1308 | CISQ Quality Measures - Security |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1337 | Weaknesses in the 2021 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1340 | CISQ Data Protection Measures |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1347 | OWASP Top Ten 2021 Category A03:2021 - Injection |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1350 | Weaknesses in the 2020 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1387 | Weaknesses in the 2022 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1409 | Comprehensive Categorization: Injection |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1425 | Weaknesses in the 2023 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1430 | Weaknesses in the 2024 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1435 | Weaknesses in the 2025 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1440 | OWASP Top Ten 2025 Category A05:2025 - Injection |

Vulnerability Mapping Notes

|  |  |
| --- | --- |
| Usage | **ALLOWED**  (this CWE ID may be used to map to real-world vulnerabilities) |
| Reason | Acceptable-Use |
| Rationale | This CWE entry is at the Base level of abstraction, which is a preferred level of abstraction for mapping to the root causes of vulnerabilities. |
| Comments | Carefully read both the name and description to ensure that this mapping is an appropriate fit. Do not try to 'force' a mapping to a lower-level Base/Variant simply to comply with this preferred level of abstraction. |

Notes

Relationship

SQL injection can be resultant from special character mismanagement, MAID, or denylist/allowlist problems. It can be primary to authentication errors.

Taxonomy
Mappings

| Mapped Taxonomy Name | Node ID | Fit | Mapped Node Name |
| --- | --- | --- | --- |
| PLOVER |  |  | SQL injection |
| 7 Pernicious Kingdoms |  |  | SQL Injection |
| CLASP |  |  | SQL injection |
| OWASP Top Ten 2007 | A2 | CWE More Specific | Injection Flaws |
| OWASP Top Ten 2004 | A1 | CWE More Specific | Unvalidated Input |
| OWASP Top Ten 2004 | A6 | CWE More Specific | Injection Flaws |
| WASC | 19 |  | SQL Injection |
| Software Fault Patterns | SFP24 |  | Tainted input to command |
| OMG ASCSM | ASCSM-CWE-89 |  |  |
| SEI CERT Oracle Coding Standard for Java | IDS00-J | Exact | Prevent SQL injection |

Related Attack Patterns

| CAPEC-ID | Attack Pattern Name |
| --- | --- |
| CAPEC-108 | Command Line Execution through SQL Injection |
| CAPEC-109 | Object Relational Mapping Injection |
| CAPEC-110 | SQL Injection through SOAP Parameter Tampering |
| CAPEC-470 | Expanding Control over the Operating System from the Database |
| CAPEC-66 | SQL Injection |
| CAPEC-7 | Blind SQL Injection |

References

|  |  |
| --- | --- |
|

[REF-1460] | rain.forest.puppy. *"NT Web Technology Vulnerabilities".* Phrack Issue 54, Volume 8. 1998-12-25.  <https://phrack.org/issues/54/8>. (*URL validated: 2025-07-24*) |

|

[REF-44] | Michael Howard, David LeBlanc and John Viega. *"24 Deadly Sins of Software Security".* "Sin 1: SQL Injection." Page 3. McGraw-Hill. 2010. |

|

[REF-7] | Michael Howard and David LeBlanc. *"Writing Secure Code".* Chapter 12, "Database Input Issues" Page 397. 2nd Edition. Microsoft Press. 2002-12-04.  <https://www.microsoftpressstore.com/store/writing-secure-code-9780735617223>. |

|

[REF-867] | OWASP. *"SQL Injection Prevention Cheat Sheet".*  <https://cheatsheetseries.owasp.org/cheatsheets/SQL\_Injection\_Prevention\_Cheat\_Sheet.html>. (*URL validated: 2025-08-04*) |

|

[REF-868] | Steven Friedl. *"SQL Injection Attacks by Example".* 2007-10-10.  <http://www.unixwiz.net/techtips/sql-injection.html>. |

|

[REF-869] | Ferruh Mavituna. *"SQL Injection Cheat Sheet".* 2007-03-15.  <https://web.archive.org/web/20080126180244/http://ferruh.mavituna.com/sql-injection-cheatsheet-oku/>. (*URL validated: 2023-04-07*) |

|

[REF-870] | David Litchfield, Chris Anley, John Heasman and Bill Grindlay. *"The Database Hacker's Handbook: Defending Database Servers".* Wiley. 2005-07-14. |

|

[REF-871] | David Litchfield. *"The Oracle Hacker's Handbook: Hacking and Defending Oracle".* Wiley. 2007-01-30. |

|

[REF-872] | Microsoft. *"SQL Injection".* 2008-12.  <https://learn.microsoft.com/en-us/previous-versions/sql/sql-server-2008-r2/ms161953(v=sql.105)?redirectedfrom=MSDN>. (*URL validated: 2023-04-07*) |

|

[REF-873] | Microsoft Security Vulnerability Research & Defense. *"SQL Injection Attack".*  <https://msrc.microsoft.com/blog/2008/05/sql-injection-attack/>. (*URL validated: 2023-04-07*) |

|

[REF-874] | Michael Howard. *"Giving SQL Injection the Respect it Deserves".* 2008-05-15.  <https://learn.microsoft.com/en-us/archive/blogs/michael\_howard/giving-sql-injection-the-respect-it-deserves>. (*URL validated: 2023-04-07*) |

|

[REF-875] | Frank Kim. *"Top 25 Series - Rank 2 - SQL Injection".* SANS Software Security Institute. 2010-03-01.  <https://www.sans.org/blog/top-25-series-rank-2-sql-injection/>. (*URL validated: 2023-04-07*) |

|

[REF-76] | Sean Barnum and Michael Gegick. *"Least Privilege".* 2005-09-14.  <https://web.archive.org/web/20211209014121/https://www.cisa.gov/uscert/bsi/articles/knowledge/principles/least-privilege>. (*URL validated: 2023-04-07*) |

|

[REF-62] | Mark Dowd, John McDonald and Justin Schuh. *"The Art of Software Security Assessment".* Chapter 8, "SQL Queries", Page 431. 1st Edition. Addison Wesley. 2006. |

|

[REF-62] | Mark Dowd, John McDonald and Justin Schuh. *"The Art of Software Security Assessment".* Chapter 17, "SQL Injection", Page 1061. 1st Edition. Addison Wesley. 2006. |

|

[REF-962] | Object Management Group (OMG). *"Automated Source Code Security Measure (ASCSM)".* ASCSM-CWE-89. 2016-01.  <http://www.omg.org/spec/ASCSM/1.0/>. |

|

[REF-1447] | Cybersecurity and Infrastructure Security Agency. *"Secure by Design Alert: Eliminating SQL Injection Vulnerabilities in Software".* 2024-03-25.  <https://www.cisa.gov/resources-tools/resources/secure-design-alert-eliminating-sql-injection-vulnerabilities-software>. (*URL validated: 2024-07-14*) |

|

[REF-1479] | Gregory Larsen, E. Kenneth Hong Fong, David A. Wheeler and Rama S. Moorthy. *"State-of-the-Art Resources (SOAR) for Software Vulnerability Detection, Test, and Evaluation".* 2014-07.  <https://www.ida.org/-/media/feature/publications/s/st/stateoftheart-resources-soar-for-software-vulnerability-detection-test-and-evaluation/p-5061.ashx>. (*URL validated: 2025-09-05*) |

|

[REF-1481] | D3FEND. *"D3FEND: Application Layer Firewall".*  <https://d3fend.mitre.org/dao/artifact/d3f:ApplicationLayerFirewall/>. (*URL validated: 2025-09-06*) |

|

[REF-1482] | D3FEND. *"D3FEND: D3-TL Trusted Library".*  <https://d3fend.mitre.org/technique/d3f:TrustedLibrary/>. (*URL validated: 2025-09-06*) |

Content
History

| Submissions | | |
| --- | --- | --- |
| Submission Date | Submitter | Organization |
| --- | --- | --- |
| 2006-07-19  (CWE Draft 3, 2006-07-19) | PLOVER |  |
|  | |
| Contributions | | |
| --- | --- | --- |
| Contribution Date | Contributor | Organization |
| --- | --- | --- |
| 2024-02-29  (CWE 4.15, 2024-07-16) | Abhi Balakrishnan |  |
| *Provided diagram to improve CWE usability* | |
| Modifications | | |
| --- | --- | --- |
| Modification Date | Modifier | Organization |
| --- | --- | --- |
| 2025-12-11  (CWE 4.19, 2025-12-11) | CWE Content Team | MITRE |
| *updated Observed\_Examples, Relationships, Weakness\_Ordinalities* | |
| 2025-09-09  (CWE 4.18, 2025-09-09) | CWE Content Team | MITRE |
| *updated Detection\_Factors, Potential\_Mitigations, References* | |
| 2025-04-03  (CWE 4.17, 2025-04-03) | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Demonstrative\_Examples, References* | |
| 2024-11-19  (CWE 4.16, 2024-11-19) | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2024-07-16  (CWE 4.15, 2024-07-16) | CWE Content Team | MITRE |
| *updated Alternate\_Terms, Common\_Consequences, Description, Diagram, References* | |
| 2024-02-29  (CWE 4.14, 2024-02-29) | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Observed\_Examples* | |
| 2023-06-29 | CWE Content Team | MITRE |
| *updated Mapping\_Notes, Relationships* | |
| 2023-04-27 | CWE Content Team | MITRE |
| *updated References, Relationships, Time\_of\_Introduction* | |
| 2023-01-31 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Description* | |
| 2022-10-13 | CWE Content Team | MITRE |
| *updated Observed\_Examples, References* | |
| 2022-06-28 | CWE Content Team | MITRE |
| *updated Observed\_Examples, Relationships* | |
| 2021-10-28 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2021-07-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2020-12-10 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, Relationships* | |
| 2020-08-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2020-06-25 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Potential\_Mitigations, Relationship\_Notes* | |
| 2020-02-24 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, Relationships, Time\_of\_Introduction* | |
| 2019-09-19 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2019-06-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2019-01-03 | CWE Content Team | MITRE |
| *updated References, Relationships, Taxonomy\_Mappings* | |
| 2018-03-27 | CWE Content Team | MITRE |
| *updated References, Relationships* | |
| 2017-11-08 | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Demonstrative\_Examples, Enabling\_Factors\_for\_Exploitation, Likelihood\_of\_Exploit, Modes\_of\_Introduction, Observed\_Examples, References, Relationships, White\_Box\_Definitions* | |
| 2017-05-03 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2015-12-07 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2014-07-30 | CWE Content Team | MITRE |
| *updated Detection\_Factors, Relationships, Taxonomy\_Mappings* | |
| 2014-06-23 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2013-07-17 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2012-10-30 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2012-05-11 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, References, Related\_Attack\_Patterns, Relationships* | |
| 2011-09-13 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, References* | |
| 2011-06-27 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2011-06-01 | CWE Content Team | MITRE |
| *updated Common\_Consequences* | |
| 2011-03-29 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples* | |
| 2010-09-27 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2010-06-21 | CWE Content Team | MITRE |
| *updated Common\_Consequences, Demonstrative\_Examples, Description, Detection\_Factors, Name, Potential\_Mitigations, References, Relationships* | |
| 2010-04-05 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Potential\_Mitigations* | |
| 2010-02-16 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Detection\_Factors, Potential\_Mitigations, References, Relationships, Taxonomy\_Mappings* | |
| 2009-12-28 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2009-07-27 | CWE Content Team | MITRE |
| *updated Description, Name, White\_Box\_Definitions* | |
| 2009-07-17 | KDM Analytics |  |
| *Improved the White\_Box\_Definition* | |
| 2009-05-27 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Name, Related\_Attack\_Patterns* | |
| 2009-03-10 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2009-01-12 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Description, Enabling\_Factors\_for\_Exploitation, Modes\_of\_Introduction, Name, Observed\_Examples, Other\_Notes, Potential\_Mitigations, References, Relationships* | |
| 2008-11-24 | CWE Content Team | MITRE |
| *updated Observed\_Examples* | |
| 2008-10-14 | CWE Content Team | MITRE |
| *updated Description* | |
| 2008-09-08 | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Common\_Consequences, Modes\_of\_Introduction, Name, Relationships, Other\_Notes, Relationship\_Notes, Taxonomy\_Mappings* | |
| 2008-08-15  (CWE 1.0, 2008-09-09) |  | Veracode |
| *Suggested OWASP Top Ten 2004 mapping* | |
| 2008-08-01  (CWE 1.0, 2008-09-09) |  | KDM Analytics |
| *added/updated white box definitions* | |
| 2008-07-01  (CWE 1.0, 2008-09-09) | Eric Dalci | Cigital |
| *updated Time\_of\_Introduction* | |
| Previous Entry Names | | |
| --- | --- | --- |
| Change Date | Previous Entry Name | | |
| --- | --- | --- | --- |
| 2008-04-11 | SQL Injection | |
| 2008-09-09 | Failure to Sanitize Data into SQL Queries (aka 'SQL Injection') | |
| 2009-01-12 | Failure to Sanitize Data within SQL Queries (aka 'SQL Injection') | |
| 2009-05-27 | Failure to Preserve SQL Query Structure (aka 'SQL Injection') | |
| 2009-07-27 | Failure to Preserve SQL Query Structure ('SQL Injection') | |
| 2010-06-21 | Improper Sanitization of Special Elements used in an SQL Command ('SQL Injection') | |

More information is available — Please edit the custom filter or select a different filter.

**Page Last Updated:** 
January 21, 2026

|  |  |  |
| --- | --- | --- |
|  | | |
|  | Site Map | Terms of Use | Manage Cookies | Cookie Notice | Privacy Policy | Contact Us |  Use of the Common Weakness Enumeration (CWE™) and the associated references from this website are subject to the Terms of Use. CWE is sponsored by the U.S. Department of Homeland Security (DHS) Cybersecurity and Infrastructure Security Agency (CISA) and managed by the Homeland Security Systems Engineering and Development Institute (HSSEDI) which is operated by The MITRE Corporation (MITRE). Copyright © 2006–2026, The MITRE Corporation. CWE, CWSS, CWRAF, and the CWE logo are trademarks of The MITRE Corporation. |  |