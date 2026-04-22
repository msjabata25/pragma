Insecure Direct Object Reference Prevention - OWASP Cheat Sheet Series

Skip to content

- JAAS
- JSON Web Token for Java
- Java Security
- Key Management
- Kubernetes Security
- LDAP Injection Prevention
- LLM Prompt Injection Prevention
- Laravel
- Legacy Application Management
- Logging
- Logging Vocabulary
- MCP Security
- Mass Assignment
- Microservices Security
- Microservices based Security Arch Doc
- Mobile Application Security
- Multi Tenant Security
- Multifactor Authentication
- NPM Security
- Network Segmentation
- NoSQL Security
- NodeJS Docker
- Nodejs Security
- OAuth2
- OS Command Injection Defense
- PHP Configuration
- Password Storage
- Pinning
- Prototype Pollution Prevention
- Query Parameterization
- REST Assessment
- REST Security
- Ruby on Rails
- SAML Security
- SQL Injection Prevention
- Secrets Management
- Secure AI Model Ops
- Secure Cloud Architecture
- Secure Code Review
- Secure Product Design
- Securing Cascading Style Sheets
- Security Terminology
- Server Side Request Forgery Prevention
- Serverless FaaS Security
- Session Management
- Software Supply Chain Security
- Subdomain Takeover Prevention
- Symfony
- TLS Cipher String
- Third Party Javascript Management
- Third Party Payment Gateway Integration
- Threat Modeling
- Transaction Authorization
- Transport Layer Protection
- Transport Layer Security
- Unvalidated Redirects and Forwards
- User Privacy Protection
- Virtual Patching
- Vulnerability Disclosure
- Vulnerable Dependency Management
- WebSocket Security
- Web Service Security
- XML External Entity Prevention
- XML Security
- XSS Filter Evasion
- XS Leaks
- Zero Trust Architecture
- gRPC Security

# Insecure Direct Object Reference Prevention Cheat Sheet¶

## Introduction¶

Insecure Direct Object Reference (IDOR) is a vulnerability that arises when attackers can access or modify objects by manipulating identifiers used in a web application's URLs or parameters. It occurs due to missing access control checks, which fail to verify whether a user should be allowed to access specific data.

## Examples¶

For instance, when a user accesses their profile, the application might generate a URL like this:

```

```

The 123 in the URL is a direct reference to the user's record in the database, often represented by the primary key. If an attacker changes this number to 124 and gains access to another user's information, the application is vulnerable to Insecure Direct Object Reference. This happens because the app didn't properly check if the user had permission to view data for user 124 before displaying it.

In some cases, the identifier may not be in the URL, but rather in the POST body, as shown in the following example:

```
<form action="/update_profile" method="post">
  <!-- Other fields for updating name, email, etc. -->
  <input type="hidden" name="user_id" value="12345">
  <button type="submit">Update Profile</button>
</form>
```

In this example, the application allows users to update their profiles by submitting a form with the user ID in a hidden field. If the app doesn't perform proper access control on the server-side, attackers can manipulate the "user\_id" field to modify profiles of other users without authorization.

## Identifier complexity¶

In some cases, using more complex identifiers like GUIDs can make it practically impossible for attackers to guess valid values. However, even with complex identifiers, access control checks are essential. If attackers obtain URLs for unauthorized objects, the application should still block their access attempts.

## Mitigation¶

To mitigate IDOR, implement access control checks for each object that users try to access. Web frameworks often provide ways to facilitate this. Additionally, use complex identifiers as a defense-in-depth measure, but remember that access control is crucial even with these identifiers.

Avoid exposing identifiers in URLs and POST bodies if possible. Instead, determine the currently authenticated user from session information. When using multi-step flows, pass identifiers in the session to prevent tampering.

When looking up objects based on primary keys, use datasets that users have access to. For example, in Ruby on Rails:

```
// vulnerable, searches all projects
@project = Project.find(params[:id])
// secure, searches projects related to the current user
@project = @current_user.projects.find(params[:id])
```

Verify the user's permission every time an access attempt is made. Implement this structurally using the recommended approach for your web framework.

As an additional defense-in-depth measure, replace enumerable numeric identifiers with more complex, random identifiers. You can achieve this by adding a column with random strings in the database table and using those strings in the URLs instead of numeric primary keys. Another option is to use UUIDs or other long random values as primary keys. Avoid encrypting identifiers as it can be challenging to do so securely.