xml version="1.0" encoding="iso-8859-1"?

CWE -
CWE-94: Improper Control of Generation of Code ('Code Injection') (4.19.1)

# Common Weakness Enumeration

A community-developed list of SW & HW weaknesses that can become vulnerabilities

|  |  |
| --- | --- |
| Home > CWE List > CWE-94: Improper Control of Generation of Code ('Code Injection') (4.19.1) |  |

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
| |  |  | | --- | --- | | CWE Glossary Definition |  | |  | |        CWE-94: Improper Control of Generation of Code ('Code Injection')  |  | | --- | | Weakness ID: 94   Vulnerability Mapping: ALLOWED This CWE ID could be used to map to real-world vulnerabilities in limited situations requiring careful review (with careful review of mapping notes)   Abstraction: Base Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. |  View customized information:  For users who are interested in more notional aspects of a weakness. Example: educators, technical writers, and project/program managers.  For users who are concerned with the practical application and details about the nature of a weakness and how to prevent it from happening. Example: tool developers, security researchers, pen-testers, incident response analysts.  For users who are mapping an issue to CWE/CAPEC IDs, i.e., finding the most appropriate CWE for a specific issue (e.g., a CVE record). Example: tool developers, security researchers.  For users who wish to see all available information for the CWE/CAPEC entry.  For users who want to customize what details are displayed.  ×  Edit Custom Filter  Description  |  |  | | --- | --- | | The product constructs all or part of a code segment using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the syntax or behavior of the intended code segment. |  |  Alternate Terms  |  |  | | --- | --- | | Code Injection |  |  Common Consequences  This table specifies different individual consequences associated with the weakness. The Scope identifies the application security area that is violated, while the Impact describes the negative technical impact that arises if an adversary succeeds in exploiting this weakness. The Likelihood provides information about how likely the specific consequence is expected to be seen relative to the other consequences in the list. For example, there may be high likelihood that a weakness will be exploited to achieve a certain impact, but a low likelihood that it will be exploited to achieve a different impact.  | Impact | Details | | --- | --- | | *Bypass Protection Mechanism* | Scope: Access Control   In some cases, injectable code controls authentication; this may lead to a remote vulnerability. | | *Gain Privileges or Assume Identity* | Scope: Access Control   Injected code can access resources that the attacker is directly prevented from accessing. | | *Execute Unauthorized Code or Commands* | Scope: Integrity, Confidentiality, Availability   When a product allows a user's input to contain code syntax, it might be possible for an attacker to craft the code in such a way that it will alter the intended control flow of the product. As a result, code injection can often result in the execution of arbitrary code. Code injection attacks can also lead to loss of data integrity in nearly all cases, since the control-plane data injected is always incidental to data recall or writing. | | *Hide Activities* | Scope: Non-Repudiation   Often the actions performed by injected control code are unlogged. |  Potential Mitigations  | Phase(s) | Mitigation | | --- | --- | | Architecture and Design | Refactor your program so that you do not have to dynamically generate code. | | Architecture and Design | Run your code in a "jail" or similar sandbox environment that enforces strict boundaries between the process and the operating system. This may effectively restrict which code can be executed by your product.  Examples include the Unix chroot jail and AppArmor. In general, managed code may provide some protection.  This may not be a feasible solution, and it only limits the impact to the operating system; the rest of your application may still be subject to compromise.  Be careful to avoid CWE-243 and other weaknesses related to jails. | | Implementation | Strategy: *Input Validation*  Assume all input is malicious. Use an "accept known good" input validation strategy, i.e., use a list of acceptable inputs that strictly conform to specifications. Reject any input that does not strictly conform to specifications, or transform it into something that does.  When performing input validation, consider all potentially relevant properties, including length, type of input, the full range of acceptable values, missing or extra inputs, syntax, consistency across related fields, and conformance to business rules. As an example of business rule logic, "boat" may be syntactically valid because it only contains alphanumeric characters, but it is not valid if the input is only expected to contain colors such as "red" or "blue."  Do not rely exclusively on looking for malicious or malformed inputs. This is likely to miss at least one undesirable input, especially if the code's environment changes. This can give attackers enough room to bypass the intended validation. However, denylists can be useful for detecting potential attacks or determining which inputs are so malformed that they should be rejected outright.  To reduce the likelihood of code injection, use stringent allowlists that limit which constructs are allowed. If you are dynamically constructing code that invokes a function, then verifying that the input is alphanumeric might be insufficient. An attacker might still be able to reference a dangerous function that you did not intend to allow, such as system(), exec(), or exit(). | | Testing | Use automated static analysis tools that target this type of weakness. Many modern techniques use data flow analysis to minimize the number of false positives. This is not a perfect solution, since 100% accuracy and coverage are not feasible. | | Testing | Use dynamic tools and techniques that interact with the product using large test suites with many diverse inputs, such as fuzz testing (fuzzing), robustness testing, and fault injection. The product's operation may slow down, but it should not become unstable, crash, or generate incorrect results. | | Operation | Strategy: *Compilation or Build Hardening*  Run the code in an environment that performs automatic taint propagation and prevents any command execution that uses tainted variables, such as Perl's "-T" switch. This will force the program to perform validation steps that remove the taint, although you must be careful to correctly validate your inputs so that you do not accidentally mark dangerous inputs as untainted (see CWE-183 and CWE-184). | | Operation | Strategy: *Environment Hardening*  Run the code in an environment that performs automatic taint propagation and prevents any command execution that uses tainted variables, such as Perl's "-T" switch. This will force the program to perform validation steps that remove the taint, although you must be careful to correctly validate your inputs so that you do not accidentally mark dangerous inputs as untainted (see CWE-183 and CWE-184). | | Implementation | For Python programs, it is frequently encouraged to use the ast.literal\_eval() function instead of eval, since it is intentionally designed to avoid executing code. However, an adversary could still cause excessive memory or stack consumption via deeply nested structures [REF-1372], so the python documentation discourages use of ast.literal\_eval() on untrusted data [REF-1373].  Effectiveness: Discouraged Common Practice |  Relationships  This table shows the weaknesses and high level categories that are related to this weakness. These relationships are defined as ChildOf, ParentOf, MemberOf and give insight to similar items that may exist at higher and lower levels of abstraction. In addition, relationships such as PeerOf and CanAlsoBe are defined to show similar weaknesses that the user may want to explore.  Relevant to the view "Research Concepts" (View-1000) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 74 | Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection') | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 913 | Improper Control of Dynamically-Managed Code Resources | | ParentOf | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 95 | Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection') | | ParentOf | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 96 | Improper Neutralization of Directives in Statically Saved Code ('Static Code Injection') | | ParentOf | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 1336 | Improper Neutralization of Special Elements Used in a Template Engine | | CanFollow | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 98 | Improper Control of Filename for Include/Require Statement in PHP Program ('PHP Remote File Inclusion') |  Relevant to the view "Software Development" (View-699) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 137 | Data Neutralization Issues |  Relevant to the view "Weaknesses for Simplified Mapping of Published Vulnerabilities" (View-1003) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 74 | Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection') |  Relevant to the view "Architectural Concepts" (View-1008) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1019 | Validate Inputs |  Modes Of Introduction  The different Modes of Introduction provide information about how and when this weakness may be introduced. The Phase identifies a point in the life cycle at which introduction may occur, while the Note provides a typical scenario related to introduction during the given phase.  | Phase | Note | | --- | --- | | Implementation | REALIZATION: This weakness is caused during implementation of an architectural security tactic. |  Applicable Platforms  This listing shows possible areas for which the given weakness could appear. These may be for specific named Languages, Operating Systems, Architectures, Paradigms, Technologies, or a class of such platforms. The platform is listed along with how frequently the given weakness appears for that instance.  |  |  | | --- | --- | | Languages | Class: Interpreted (Sometimes Prevalent) | | Technologies | AI/ML (Undetermined Prevalence) |  Likelihood Of Exploit  Medium  Demonstrative Examples  Example 1  Selected Observed Examples  *Note: this is a curated list of examples for users to understand the variety of ways in which this weakness can be introduced. It is not a complete list of all CVEs that are related to this CWE entry.*  | Reference | Description | | --- | --- | | CVE-2023-29374 | Math component in an LLM framework translates user input into a Python expression that is input into the Python exec() method, allowing code execution - one variant of a "prompt injection" attack. | | CVE-2024-5565 | Python-based library uses an LLM prompt containing user input to dynamically generate code that is then fed as input into the Python exec() method, allowing code execution - one variant of a "prompt injection" attack. | | CVE-2024-4181 | Framework for LLM applications allows eval injection via a crafted response from a hosting provider. | | CVE-2022-2054 | Python compiler uses eval() to execute malicious strings as Python code. | | CVE-2021-22204 | Chain: regex in EXIF processor code does not correctly determine where a string ends (CWE-625), enabling eval injection (CWE-95), as exploited in the wild per CISA KEV. | | CVE-2020-8218 | "Code injection" in VPN product, as exploited in the wild per CISA KEV. | | CVE-2008-5071 | Eval injection in PHP program. | | CVE-2002-1750 | Eval injection in Perl program. | | CVE-2008-5305 | Eval injection in Perl program using an ID that should only contain hyphens and numbers. | | CVE-2002-1752 | Direct code injection into Perl eval function. | | CVE-2002-1753 | Eval injection in Perl program. | | CVE-2005-1527 | Direct code injection into Perl eval function. | | CVE-2005-2837 | Direct code injection into Perl eval function. | | CVE-2005-1921 | MFV. code injection into PHP eval statement using nested constructs that should not be nested. | | CVE-2005-2498 | MFV. code injection into PHP eval statement using nested constructs that should not be nested. | | CVE-2005-3302 | Code injection into Python eval statement from a field in a formatted file. | | CVE-2007-1253 | Eval injection in Python program. | | CVE-2001-1471 | chain: Resultant eval injection. An invalid value prevents initialization of variables, which can be modified by attacker and later injected into PHP eval statement. | | CVE-2002-0495 | Perl code directly injected into CGI library file from parameters to another CGI program. | | CVE-2005-1876 | Direct PHP code injection into supporting template file. | | CVE-2005-1894 | Direct code injection into PHP script that can be accessed by attacker. | | CVE-2003-0395 | PHP code from User-Agent HTTP header directly inserted into log file implemented as PHP script. |  Weakness Ordinalities  | Ordinality | Description | | --- | --- | | Primary | (where the weakness exists independent of other weaknesses) |  Resultant | (where the weakness is typically related to the presence of some other weaknesses) | |

Detection
Methods

| Method | Details |
| --- | --- |
| Automated Static Analysis | Automated static analysis, commonly referred to as Static Application Security Testing (SAST), can find some instances of this weakness by analyzing source code (or binary/compiled code) without having to execute it. Typically, this is done by building a model of data flow and control flow, then searching for potentially-vulnerable patterns that connect "sources" (origins of input) with "sinks" (destinations where the data interacts with external components, a lower layer such as the OS, etc.)  Effectiveness: High |

Memberships

This MemberOf Relationships table shows additional CWE Categories and Views that
reference this weakness as a member. This information is often useful in understanding where a
weakness fits within the context of external information sources.

| Nature | Type | ID | Name |
| --- | --- | --- | --- |
|  |  |  |  |
| --- | --- | --- | --- |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 635 | Weaknesses Originally Used by NVD from 2008 to 2016 |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 752 | 2009 Top 25 - Risky Resource Management |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 884 | CWE Cross-section |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 991 | SFP Secondary Cluster: Tainted Input to Environment |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1200 | Weaknesses in the 2019 CWE Top 25 Most Dangerous Software Errors |
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
| Usage | **ALLOWED-WITH-REVIEW**  (this CWE ID could be used to map to real-world vulnerabilities in limited situations requiring careful review) |
| Reasons | Frequent Misuse, Frequent Misinterpretation |
| Rationale | This entry is frequently misused for vulnerabilities with a technical impact of "code execution," which does not by itself indicate a root cause weakness, since dozens of weaknesses can enable code execution. |
| Comments | This weakness only applies when the product's functionality intentionally constructs all or part of a code segment. It could be that executing code could be the result of other weaknesses that do not involve the construction of code segments. |

Notes

Theoretical

Injection problems encompass a wide variety of issues -- all mitigated in very different ways. For this reason, the most effective way to discuss these weaknesses is to note the distinct features that classify them as injection weaknesses. The most important issue to note is that all injection problems share one thing in common -- i.e., they allow for the injection of control plane data into the user-controlled data plane. This means that the execution of the process may be altered by sending code in through legitimate data channels, using no other mechanism. While buffer overflows, and many other flaws, involve the use of some further issue to gain execution, injection problems need only for the data to be parsed. The most classic instantiations of this category of weakness are SQL injection and format string vulnerabilities.

Taxonomy
Mappings

| Mapped Taxonomy Name | Node ID | Fit | Mapped Node Name |
| --- | --- | --- | --- |
| PLOVER | CODE |  | Code Evaluation and Injection |
| ISA/IEC 62443 | Part 4-2 |  | Req CR 3.5 |
| ISA/IEC 62443 | Part 3-3 |  | Req SR 3.5 |
| ISA/IEC 62443 | Part 4-1 |  | Req SVV-1 |
| ISA/IEC 62443 | Part 4-1 |  | Req SVV-3 |

Related Attack Patterns

| CAPEC-ID | Attack Pattern Name |
| --- | --- |
| CAPEC-242 | Code Injection |
| CAPEC-35 | Leverage Executable Code in Non-Executable Files |
| CAPEC-77 | Manipulating User-Controlled Variables |

References

|  |  |
| --- | --- |
|

[REF-44] | Michael Howard, David LeBlanc and John Viega. *"24 Deadly Sins of Software Security".* "Sin 3: Web-Client Related Vulnerabilities (XSS)." Page 63. McGraw-Hill. 2010. |

|

[REF-1372] | *"How ast.literal\_eval can cause memory exhaustion".* Reddit. 2022-12-14.  <https://www.reddit.com/r/learnpython/comments/zmbhcf/how\_astliteral\_eval\_can\_cause\_memory\_exhaustion/>. (*URL validated: 2023-11-03*) |

|

[REF-1373] | *"ast - Abstract Syntax Trees".* ast.literal\_eval(node\_or\_string). Python. 2023-11-02.  <https://docs.python.org/3/library/ast.html#ast.literal\_eval>. (*URL validated: 2023-11-03*) |

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
| 2023-06-29  (CWE 4.12, 2023-06-29) | "Mapping CWE to 62443" Sub-Working Group | CWE-CAPEC ICS/OT SIG |
| *Suggested mappings to ISA/IEC 62443.* | |
| 2024-02-29  (CWE 4.17, 2025-04-03) | Abhi Balakrishnan |  |
| *Contributed usability diagram concepts used by the CWE team.* | |
| 2025-08-22  (CWE 4.19, 2025-12-11) | Matthew A. Pagan | Spectrum |
| *Discovered a syntax issue in the Python3 demox (DX-156) and suggested a fix* | |
| Modifications | | |
| --- | --- | --- |
| Modification Date | Modifier | Organization |
| --- | --- | --- |
| 2025-12-11  (CWE 4.19, 2025-12-11) | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Relationships, Weakness\_Ordinalities* | |
| 2025-04-03  (CWE 4.17, 2025-04-03) | CWE Content Team | MITRE |
| *updated Alternate\_Terms, Common\_Consequences, Description, Diagram, Theoretical\_Notes* | |
| 2024-11-19  (CWE 4.16, 2024-11-19) | CWE Content Team | MITRE |
| *updated Mapping\_Notes, Relationships* | |
| 2024-07-16  (CWE 4.15, 2024-07-16) | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Observed\_Examples* | |
| 2024-02-29  (CWE 4.14, 2024-02-29) | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Potential\_Mitigations, References* | |
| 2023-06-29 | CWE Content Team | MITRE |
| *updated Mapping\_Notes, Relationships, Taxonomy\_Mappings* | |
| 2023-04-27 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Detection\_Factors, Relationships, Time\_of\_Introduction* | |
| 2023-01-31 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Description, Potential\_Mitigations, Relationships* | |
| 2022-10-13 | CWE Content Team | MITRE |
| *updated Observed\_Examples* | |
| 2022-06-28 | CWE Content Team | MITRE |
| *updated Observed\_Examples, Relationships* | |
| 2022-04-28 | CWE Content Team | MITRE |
| *updated Research\_Gaps* | |
| 2021-10-28 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2021-07-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2021-03-15 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples* | |
| 2020-08-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2020-06-25 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2020-02-24 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, Relationships* | |
| 2019-09-19 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2019-06-20 | CWE Content Team | MITRE |
| *updated Related\_Attack\_Patterns, Type* | |
| 2017-11-08 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Modes\_of\_Introduction, Relationships* | |
| 2015-12-07 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2014-07-30 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2013-02-21 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2012-10-30 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2012-05-11 | CWE Content Team | MITRE |
| *updated Common\_Consequences, Demonstrative\_Examples, Observed\_Examples, References, Relationships* | |
| 2011-06-01 | CWE Content Team | MITRE |
| *updated Common\_Consequences* | |
| 2011-03-29 | CWE Content Team | MITRE |
| *updated Name* | |
| 2010-06-21 | CWE Content Team | MITRE |
| *updated Description, Potential\_Mitigations* | |
| 2010-02-16 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2009-05-27 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples, Name* | |
| 2009-03-10 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2009-01-12 | CWE Content Team | MITRE |
| *updated Common\_Consequences, Demonstrative\_Examples, Description, Likelihood\_of\_Exploit, Name, Potential\_Mitigations, Relationships* | |
| 2008-09-08 | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Relationships, Research\_Gaps, Taxonomy\_Mappings* | |
| 2008-07-01 | Eric Dalci | Cigital |
| *updated Time\_of\_Introduction* | |
| Previous Entry Names | | |
| --- | --- | --- |
| Change Date | Previous Entry Name | | |
| --- | --- | --- | --- |
| 2009-01-12 | Code Injection | |
| 2009-05-27 | Failure to Control Generation of Code (aka 'Code Injection') | |
| 2011-03-29 | Failure to Control Generation of Code ('Code Injection') | |

More information is available — Please edit the custom filter or select a different filter.

**Page Last Updated:** 
January 21, 2026

|  |  |  |
| --- | --- | --- |
|  | | |
|  | Site Map | Terms of Use | Manage Cookies | Cookie Notice | Privacy Policy | Contact Us |  Use of the Common Weakness Enumeration (CWE™) and the associated references from this website are subject to the Terms of Use. CWE is sponsored by the U.S. Department of Homeland Security (DHS) Cybersecurity and Infrastructure Security Agency (CISA) and managed by the Homeland Security Systems Engineering and Development Institute (HSSEDI) which is operated by The MITRE Corporation (MITRE). Copyright © 2006–2026, The MITRE Corporation. CWE, CWSS, CWRAF, and the CWE logo are trademarks of The MITRE Corporation. |  |