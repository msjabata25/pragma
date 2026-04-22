xml version="1.0" encoding="iso-8859-1"?

CWE -
CWE-434: Unrestricted Upload of File with Dangerous Type (4.19.1)

# Common Weakness Enumeration

A community-developed list of SW & HW weaknesses that can become vulnerabilities

|  |  |
| --- | --- |
| Home > CWE List > CWE-434: Unrestricted Upload of File with Dangerous Type (4.19.1) |  |

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
| |  |  | | --- | --- | | CWE Glossary Definition |  | |  | |        CWE-434: Unrestricted Upload of File with Dangerous Type  |  | | --- | | Weakness ID: 434   Vulnerability Mapping: ALLOWED This CWE ID may be used to map to real-world vulnerabilities   Abstraction: Base Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. |  View customized information:  For users who are interested in more notional aspects of a weakness. Example: educators, technical writers, and project/program managers.  For users who are concerned with the practical application and details about the nature of a weakness and how to prevent it from happening. Example: tool developers, security researchers, pen-testers, incident response analysts.  For users who are mapping an issue to CWE/CAPEC IDs, i.e., finding the most appropriate CWE for a specific issue (e.g., a CVE record). Example: tool developers, security researchers.  For users who wish to see all available information for the CWE/CAPEC entry.  For users who want to customize what details are displayed.  ×  Edit Custom Filter  Description  |  |  | | --- | --- | | The product allows the upload or transfer of dangerous file types that are automatically processed within its environment. |  |  Alternate Terms  |  |  | | --- | --- | | Unrestricted File Upload | Used in vulnerability databases and elsewhere, but it is insufficiently precise. The phrase could be interpreted as the lack of restrictions on the size or number of uploaded files, which is a resource consumption issue. |  Common Consequences  This table specifies different individual consequences associated with the weakness. The Scope identifies the application security area that is violated, while the Impact describes the negative technical impact that arises if an adversary succeeds in exploiting this weakness. The Likelihood provides information about how likely the specific consequence is expected to be seen relative to the other consequences in the list. For example, there may be high likelihood that a weakness will be exploited to achieve a certain impact, but a low likelihood that it will be exploited to achieve a different impact.  | Impact | Details | | --- | --- | | *Execute Unauthorized Code or Commands* | Scope: Integrity, Confidentiality, Availability   Arbitrary code execution is possible if an uploaded file is interpreted and executed as code by the recipient. This is especially true for web-server extensions such as .asp and .php because these file types are often treated as automatically executable, even when file system permissions do not specify execution. For example, in Unix environments, programs typically cannot run unless the execute bit is set, but PHP programs may be executed by the web server without directly invoking them on the operating system. |  Potential Mitigations  | Phase(s) | Mitigation | | --- | --- | | Architecture and Design | Generate a new, unique filename for an uploaded file instead of using the user-supplied filename, so that no external input is used at all.[REF-422] [REF-423] | | Architecture and Design | Strategy: *Enforcement by Conversion*  When the set of acceptable objects, such as filenames or URLs, is limited or known, create a mapping from a set of fixed input values (such as numeric IDs) to the actual filenames or URLs, and reject all other inputs. | | Architecture and Design | Consider storing the uploaded files outside of the web document root entirely. Then, use other mechanisms to deliver the files dynamically. [REF-423] | | Implementation | Strategy: *Input Validation*  Assume all input is malicious. Use an "accept known good" input validation strategy, i.e., use a list of acceptable inputs that strictly conform to specifications. Reject any input that does not strictly conform to specifications, or transform it into something that does.  When performing input validation, consider all potentially relevant properties, including length, type of input, the full range of acceptable values, missing or extra inputs, syntax, consistency across related fields, and conformance to business rules. As an example of business rule logic, "boat" may be syntactically valid because it only contains alphanumeric characters, but it is not valid if the input is only expected to contain colors such as "red" or "blue."  Do not rely exclusively on looking for malicious or malformed inputs. This is likely to miss at least one undesirable input, especially if the code's environment changes. This can give attackers enough room to bypass the intended validation. However, denylists can be useful for detecting potential attacks or determining which inputs are so malformed that they should be rejected outright.  For example, limiting filenames to alphanumeric characters can help to restrict the introduction of unintended file extensions. | | Architecture and Design | Define a very limited set of allowable extensions and only generate filenames that end in these extensions. Consider the possibility of XSS (CWE-79) before allowing .html or .htm file types. | | Implementation | Strategy: *Input Validation*  Ensure that only one extension is used in the filename. Some web servers, including some versions of Apache, may process files based on inner extensions so that "filename.php.gif" is fed to the PHP interpreter.[REF-422] [REF-423] | | Implementation | When running on a web server that supports case-insensitive filenames, perform case-insensitive evaluations of the extensions that are provided. | | Architecture and Design | For any security checks that are performed on the client side, ensure that these checks are duplicated on the server side, in order to avoid CWE-602. Attackers can bypass the client-side checks by modifying values after the checks have been performed, or by changing the client to remove the client-side checks entirely. Then, these modified values would be submitted to the server. | | Implementation | Do not rely exclusively on sanity checks of file contents to ensure that the file is of the expected type and size. It may be possible for an attacker to hide code in some file segments that will still be executed by the server. For example, GIF images may contain a free-form comments field. | | Implementation | Do not rely exclusively on the MIME content type or filename attribute when determining how to render a file. Validating the MIME content type and ensuring that it matches the extension is only a partial solution. | | Architecture and Design; Operation | Strategy: *Environment Hardening*  Run your code using the lowest privileges that are required to accomplish the necessary tasks [REF-76]. If possible, create isolated accounts with limited privileges that are only used for a single task. That way, a successful attack will not immediately give the attacker access to the rest of the software or its environment. For example, database applications rarely need to run as the database administrator, especially in day-to-day operations. | | Architecture and Design; Operation | Strategy: *Sandbox or Jail*  Run the code in a "jail" or similar sandbox environment that enforces strict boundaries between the process and the operating system. This may effectively restrict which files can be accessed in a particular directory or which commands can be executed by the software.  OS-level examples include the Unix chroot jail, AppArmor, and SELinux. In general, managed code may provide some protection. For example, java.io.FilePermission in the Java SecurityManager allows the software to specify restrictions on file operations.  This may not be a feasible solution, and it only limits the impact to the operating system; the rest of the application may still be subject to compromise.  Be careful to avoid CWE-243 and other weaknesses related to jails.  Effectiveness: Limited  **Note:**  The effectiveness of this mitigation depends on the prevention capabilities of the specific sandbox or jail being used and might only help to reduce the scope of an attack, such as restricting the attacker to certain system calls or limiting the portion of the file system that can be accessed. |  Relationships  This table shows the weaknesses and high level categories that are related to this weakness. These relationships are defined as ChildOf, ParentOf, MemberOf and give insight to similar items that may exist at higher and lower levels of abstraction. In addition, relationships such as PeerOf and CanAlsoBe are defined to show similar weaknesses that the user may want to explore.  Relevant to the view "Research Concepts" (View-1000) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 669 | Incorrect Resource Transfer Between Spheres | | PeerOf | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 351 | Insufficient Type Distinction | | PeerOf | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 430 | Deployment of Wrong Handler | | PeerOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 436 | Interpretation Conflict | | PeerOf | Variant - a weakness that is linked to a certain type of product, typically involving a specific language or technology. More specific than a Base weakness. Variant level weaknesses typically describe issues in terms of 3 to 5 of the following dimensions: behavior, property, technology, language, and resource. | 646 | Reliance on File Name or Extension of Externally-Supplied File | | CanFollow | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 73 | External Control of File Name or Path | | CanFollow | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 183 | Permissive List of Allowed Inputs | | CanFollow | Base - a weakness that is still mostly independent of a resource or technology, but with sufficient details to provide specific methods for detection and prevention. Base level weaknesses typically describe issues in terms of 2 or 3 of the following dimensions: behavior, property, technology, language, and resource. | 184 | Incomplete List of Disallowed Inputs |  Relevant to the view "Software Development" (View-699) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 429 | Handler Errors |  Relevant to the view "Weaknesses for Simplified Mapping of Published Vulnerabilities" (View-1003) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | ChildOf | Class - a weakness that is described in a very abstract fashion, typically independent of any specific language or technology. More specific than a Pillar Weakness, but more general than a Base Weakness. Class level weaknesses typically describe issues in terms of 1 or 2 of the following dimensions: behavior, property, and resource. | 669 | Incorrect Resource Transfer Between Spheres |  Relevant to the view "Architectural Concepts" (View-1008) | Nature | Type | ID | Name | | --- | --- | --- | --- | |  |  |  |  | | --- | --- | --- | --- | | MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1011 | Authorize Actors |  Modes Of Introduction  The different Modes of Introduction provide information about how and when this weakness may be introduced. The Phase identifies a point in the life cycle at which introduction may occur, while the Note provides a typical scenario related to introduction during the given phase.  | Phase | Note | | --- | --- | | Implementation |  | | Architecture and Design | OMISSION: This weakness is caused by missing a security tactic during the architecture and design phase. |  Applicable Platforms  This listing shows possible areas for which the given weakness could appear. These may be for specific named Languages, Operating Systems, Architectures, Paradigms, Technologies, or a class of such platforms. The platform is listed along with how frequently the given weakness appears for that instance.  |  |  | | --- | --- | | Languages | ASP.NET (Sometimes Prevalent)  PHP (Often Prevalent)  Class: Not Language-Specific (Undetermined Prevalence) | | Technologies | Web Server (Sometimes Prevalent) |  Likelihood Of Exploit  Medium  Demonstrative Examples  Example 1  Selected Observed Examples  *Note: this is a curated list of examples for users to understand the variety of ways in which this weakness can be introduced. It is not a complete list of all CVEs that are related to this CWE entry.*  | Reference | Description | | --- | --- | | CVE-2023-5227 | PHP-based FAQ management app does not check the MIME type for uploaded images | | CVE-2001-0901 | Web-based mail product stores ".shtml" attachments that could contain SSI | | CVE-2002-1841 | PHP upload does not restrict file types | | CVE-2005-1868 | upload and execution of .php file | | CVE-2005-1881 | upload file with dangerous extension | | CVE-2005-0254 | program does not restrict file types | | CVE-2004-2262 | improper type checking of uploaded files | | CVE-2006-4558 | Double "php" extension leaves an active php extension in the generated filename. | | CVE-2006-6994 | ASP program allows upload of .asp files by bypassing client-side checks | | CVE-2005-3288 | ASP file upload | | CVE-2006-2428 | ASP file upload |  Weakness Ordinalities  | Ordinality | Description | | --- | --- | | Primary | (where the weakness exists independent of other weaknesses)  This can be primary when there is no check for the file type at all. |  Resultant | (where the weakness is typically related to the presence of some other weaknesses)  This can be resultant when use of double extensions (e.g. ".php.gif") bypasses a check. | |
 Resultant | (where the weakness is typically related to the presence of some other weaknesses)  This can be resultant from client-side enforcement (CWE-602); some products will include web script in web clients to check the filename, without verifying on the server side. |

Detection
Methods

| Method | Details |
| --- | --- |
| Dynamic Analysis with Automated Results Interpretation | According to SOAR [REF-1479], the following detection techniques may be useful:  Cost effective for partial coverage:   - Web Application Scanner - Web Services Scanner - Database Scanners  Effectiveness: SOAR Partial |
| Dynamic Analysis with Manual Results Interpretation | According to SOAR [REF-1479], the following detection techniques may be useful:  Cost effective for partial coverage:   - Fuzz Tester - Framework-based Fuzzer  Effectiveness: SOAR Partial |
| Manual Static Analysis - Source Code | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Focused Manual Spotcheck - Focused manual analysis of source - Manual Source Code Review (not inspections)  Effectiveness: High |
| Automated Static Analysis - Source Code | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Source code Weakness Analyzer - Context-configured Source Code Weakness Analyzer  Effectiveness: High |
| Architecture or Design Review | According to SOAR [REF-1479], the following detection techniques may be useful:  Highly cost effective:   - Formal Methods / Correct-By-Construction   Cost effective for partial coverage:   - Inspection (IEEE 1028 standard) (can apply to requirements, design, source code, etc.)  Effectiveness: High |

Functional Areas

- File Processing

Affected Resources

- File or Directory

Memberships

This MemberOf Relationships table shows additional CWE Categories and Views that
reference this weakness as a member. This information is often useful in understanding where a
weakness fits within the context of external information sources.

| Nature | Type | ID | Name |
| --- | --- | --- | --- |
|  |  |  |  |
| --- | --- | --- | --- |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 714 | OWASP Top Ten 2007 Category A3 - Malicious File Execution |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 801 | 2010 Top 25 - Insecure Interaction Between Components |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 813 | OWASP Top Ten 2010 Category A4 - Insecure Direct Object References |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 864 | 2011 Top 25 - Insecure Interaction Between Components |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 884 | CWE Cross-section |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1131 | CISQ Quality Measures (2016) - Security |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1200 | Weaknesses in the 2019 CWE Top 25 Most Dangerous Software Errors |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1308 | CISQ Quality Measures - Security |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1337 | Weaknesses in the 2021 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1340 | CISQ Data Protection Measures |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1348 | OWASP Top Ten 2021 Category A04:2021 - Insecure Design |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1350 | Weaknesses in the 2020 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1364 | ICS Communications: Zone Boundary Failures |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1387 | Weaknesses in the 2022 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1416 | Comprehensive Categorization: Resource Lifecycle Management |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1425 | Weaknesses in the 2023 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1430 | Weaknesses in the 2024 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | View - a subset of CWE entries that provides a way of examining CWE content. The two main view structures are Slices (flat lists) and Graphs (containing relationships between entries). | 1435 | Weaknesses in the 2025 CWE Top 25 Most Dangerous Software Weaknesses |
| MemberOf | Category - a CWE entry that contains a set of other entries that share a common characteristic. | 1441 | OWASP Top Ten 2025 Category A06:2025 - Insecure Design |

Vulnerability Mapping Notes

|  |  |
| --- | --- |
| Usage | **ALLOWED**  (this CWE ID may be used to map to real-world vulnerabilities) |
| Reason | Acceptable-Use |
| Rationale | This CWE entry is at the Base level of abstraction, which is a preferred level of abstraction for mapping to the root causes of vulnerabilities. |
| Comments | Carefully read both the name and description to ensure that this mapping is an appropriate fit. Do not try to 'force' a mapping to a lower-level Base/Variant simply to comply with this preferred level of abstraction. |

Notes

Relationship

This can have a chaining relationship with incomplete denylist / permissive allowlist errors when the product tries, but fails, to properly limit which types of files are allowed (CWE-183, CWE-184).

This can also overlap multiple interpretation errors for intermediaries, e.g. anti-virus products that do not remove or quarantine attachments with certain file extensions that can be processed by client systems.

Taxonomy
Mappings

| Mapped Taxonomy Name | Node ID | Fit | Mapped Node Name |
| --- | --- | --- | --- |
| PLOVER |  |  | Unrestricted File Upload |
| OWASP Top Ten 2007 | A3 | CWE More Specific | Malicious File Execution |
| OMG ASCSM | ASCSM-CWE-434 |  |  |

Related Attack Patterns

| CAPEC-ID | Attack Pattern Name |
| --- | --- |
| CAPEC-1 | Accessing Functionality Not Properly Constrained by ACLs |

References

|  |  |
| --- | --- |
|

[REF-422] | Richard Stanway (r1CH). *"Dynamic File Uploads, Security and You".*  <https://web.archive.org/web/20090208005456/http://shsc.info/FileUploadSecurity>. (*URL validated: 2025-07-24*) |

|

[REF-423] | Johannes Ullrich. *"8 Basic Rules to Implement Secure File Uploads".* 2009-12-28.  <https://www.sans.org/blog/8-basic-rules-to-implement-secure-file-uploads/>. (*URL validated: 2023-04-07*) |

|

[REF-424] | Johannes Ullrich. *"Top 25 Series - Rank 8 - Unrestricted Upload of Dangerous File Type".* SANS Software Security Institute. 2010-02-25.  <https://www.sans.org/blog/top-25-series-rank-8-unrestricted-upload-of-dangerous-file-type/>. (*URL validated: 2023-04-07*) |

|

[REF-76] | Sean Barnum and Michael Gegick. *"Least Privilege".* 2005-09-14.  <https://web.archive.org/web/20211209014121/https://www.cisa.gov/uscert/bsi/articles/knowledge/principles/least-privilege>. (*URL validated: 2023-04-07*) |

|

[REF-62] | Mark Dowd, John McDonald and Justin Schuh. *"The Art of Software Security Assessment".* Chapter 17, "File Uploading", Page 1068. 1st Edition. Addison Wesley. 2006. |

|

[REF-962] | Object Management Group (OMG). *"Automated Source Code Security Measure (ASCSM)".* ASCSM-CWE-434. 2016-01.  <http://www.omg.org/spec/ASCSM/1.0/>. |

|

[REF-1479] | Gregory Larsen, E. Kenneth Hong Fong, David A. Wheeler and Rama S. Moorthy. *"State-of-the-Art Resources (SOAR) for Software Vulnerability Detection, Test, and Evaluation".* 2014-07.  <https://www.ida.org/-/media/feature/publications/s/st/stateoftheart-resources-soar-for-software-vulnerability-detection-test-and-evaluation/p-5061.ashx>. (*URL validated: 2025-09-05*) |

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
| *updated Relationships* | |
| 2025-09-09  (CWE 4.18, 2025-09-09) | CWE Content Team | MITRE |
| *updated Detection\_Factors, References* | |
| 2024-11-19  (CWE 4.16, 2024-11-19) | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2024-07-16  (CWE 4.15, 2024-07-16) | CWE Content Team | MITRE |
| *updated Common\_Consequences, Description, Diagram, Weakness\_Ordinalities* | |
| 2024-02-29  (CWE 4.14, 2024-02-29) | CWE Content Team | MITRE |
| *updated Observed\_Examples* | |
| 2023-06-29 | CWE Content Team | MITRE |
| *updated Mapping\_Notes, Relationships* | |
| 2023-04-27 | CWE Content Team | MITRE |
| *updated References, Relationships* | |
| 2023-01-31 | CWE Content Team | MITRE |
| *updated Alternate\_Terms, Description* | |
| 2022-10-13 | CWE Content Team | MITRE |
| *updated References* | |
| 2022-06-28 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2022-04-28 | CWE Content Team | MITRE |
| *updated Research\_Gaps* | |
| 2021-10-28 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2021-07-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2021-03-15 | CWE Content Team | MITRE |
| *updated Demonstrative\_Examples* | |
| 2020-12-10 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2020-08-20 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2020-06-25 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, Relationship\_Notes* | |
| 2020-02-24 | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Potential\_Mitigations* | |
| 2019-09-19 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2019-06-20 | CWE Content Team | MITRE |
| *updated Related\_Attack\_Patterns* | |
| 2019-01-03 | CWE Content Team | MITRE |
| *updated References, Relationships, Taxonomy\_Mappings* | |
| 2017-11-08 | CWE Content Team | MITRE |
| *updated Affected\_Resources, Applicable\_Platforms, Likelihood\_of\_Exploit, Modes\_of\_Introduction, References, Relationships, Weakness\_Ordinalities* | |
| 2015-12-07 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2014-07-30 | CWE Content Team | MITRE |
| *updated Detection\_Factors* | |
| 2012-10-30 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2012-05-11 | CWE Content Team | MITRE |
| *updated References, Relationships* | |
| 2011-09-13 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations, References, Relationships* | |
| 2011-06-27 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2010-12-13 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2010-09-27 | CWE Content Team | MITRE |
| *updated Potential\_Mitigations* | |
| 2010-06-21 | CWE Content Team | MITRE |
| *updated References, Relationship\_Notes* | |
| 2010-04-05 | CWE Content Team | MITRE |
| *updated Related\_Attack\_Patterns* | |
| 2010-02-16 | CWE Content Team | MITRE |
| *updated Alternate\_Terms, Applicable\_Platforms, Common\_Consequences, Demonstrative\_Examples, Name, Other\_Notes, Potential\_Mitigations, References, Related\_Attack\_Patterns, Relationship\_Notes, Relationships, Type, Weakness\_Ordinalities* | |
| 2010-02-16 | CWE Content Team | MITRE |
| *converted from Compound\_Element to Weakness* | |
| 2009-12-28 | CWE Content Team | MITRE |
| *updated Applicable\_Platforms, Functional\_Areas, Likelihood\_of\_Exploit, Potential\_Mitigations, Time\_of\_Introduction* | |
| 2009-01-12 | CWE Content Team | MITRE |
| *updated Relationships* | |
| 2008-09-08 | CWE Content Team | MITRE |
| *updated Alternate\_Terms, Relationships, Other\_Notes, Taxonomy\_Mappings* | |
| 2008-07-01 | Eric Dalci | Cigital |
| *updated Time\_of\_Introduction* | |
| Previous Entry Names | | |
| --- | --- | --- |
| Change Date | Previous Entry Name | | |
| --- | --- | --- | --- |
| 2010-02-16 | Unrestricted File Upload | |

More information is available — Please edit the custom filter or select a different filter.

**Page Last Updated:** 
January 21, 2026

|  |  |  |
| --- | --- | --- |
|  | | |
|  | Site Map | Terms of Use | Manage Cookies | Cookie Notice | Privacy Policy | Contact Us |  Use of the Common Weakness Enumeration (CWE™) and the associated references from this website are subject to the Terms of Use. CWE is sponsored by the U.S. Department of Homeland Security (DHS) Cybersecurity and Infrastructure Security Agency (CISA) and managed by the Homeland Security Systems Engineering and Development Institute (HSSEDI) which is operated by The MITRE Corporation (MITRE). Copyright © 2006–2026, The MITRE Corporation. CWE, CWSS, CWRAF, and the CWE logo are trademarks of The MITRE Corporation. |  |