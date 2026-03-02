# Legal & Compliance Framework for Real Estate Lead Generation

> **Purpose**: Comprehensive legal reference for the TheLeadEdge system. This document covers every federal, state, and local regulation that applies to real estate lead generation and outreach. It is organized so you can quickly find compliance requirements by regulation, by outreach method, or by lead source.
>
> **Disclaimer**: This document is a research summary and does not constitute legal advice. Laws change frequently. Before launching any campaign, consult a real estate attorney licensed in your state and have all marketing materials reviewed by your managing broker.
>
> **Last Updated**: February 2026

---

## Table of Contents

1. [Federal Regulations Overview](#1-federal-regulations-overview)
   - 1.1 [Do Not Call Registry (FTC/FCC)](#11-do-not-call-registry-ftcfcc)
   - 1.2 [CAN-SPAM Act](#12-can-spam-act)
   - 1.3 [TCPA (Telephone Consumer Protection Act)](#13-tcpa-telephone-consumer-protection-act)
   - 1.4 [Fair Housing Act](#14-fair-housing-act)
   - 1.5 [FCRA (Fair Credit Reporting Act)](#15-fcra-fair-credit-reporting-act)
   - 1.6 [RESPA (Real Estate Settlement Procedures Act)](#16-respa-real-estate-settlement-procedures-act)
2. [State-Specific Regulations](#2-state-specific-regulations)
   - 2.1 [Foreclosure Solicitation Restrictions](#21-foreclosure-solicitation-restrictions)
   - 2.2 [State Do Not Call Lists](#22-state-do-not-call-lists)
   - 2.3 [State Real Estate Commission Rules](#23-state-real-estate-commission-rules)
   - 2.4 [Local Anti-Solicitation Ordinances](#24-local-anti-solicitation-ordinances)
3. [Compliance by Outreach Method](#3-compliance-by-outreach-method)
   - 3.1 [Direct Mail](#31-direct-mail)
   - 3.2 [Phone Calls](#32-phone-calls)
   - 3.3 [Email](#33-email)
   - 3.4 [Text / SMS](#34-text--sms)
   - 3.5 [Door Knocking](#35-door-knocking)
   - 3.6 [Social Media](#36-social-media)
4. [Compliance by Lead Source](#4-compliance-by-lead-source)
   - 4.1 [Pre-Foreclosure Leads](#41-pre-foreclosure-leads)
   - 4.2 [Probate Leads](#42-probate-leads)
   - 4.3 [Divorce Leads](#43-divorce-leads)
   - 4.4 [Expired & FSBO Leads](#44-expired--fsbo-leads)
   - 4.5 [Public Records Generally](#45-public-records-generally)
5. [MLS Terms of Service Compliance](#5-mls-terms-of-service-compliance)
6. [Data Privacy](#6-data-privacy)
7. [Record-Keeping Requirements](#7-record-keeping-requirements)
8. [Compliance Checklist](#8-compliance-checklist)
9. [Risk Mitigation](#9-risk-mitigation)

---

## 1. Federal Regulations Overview

### 1.1 Do Not Call Registry (FTC/FCC)

The National Do Not Call Registry is administered jointly by the Federal Trade Commission (FTC) and the Federal Communications Commission (FCC). It is the single most common source of complaints and fines for real estate agents conducting phone outreach.

#### Core Requirements

| Requirement | Detail |
|---|---|
| **Registry check** | Must scrub all call lists against the National DNC Registry before calling |
| **Access** | Register at telemarketing.donotcall.gov to download area-code-specific files |
| **Scrub frequency** | Lists must be scrubbed at least every 31 days. If your list is older than 31 days, re-scrub before calling |
| **Internal DNC list** | Must maintain your own company-specific DNC list of anyone who has asked not to be called |
| **Internal list duration** | Requests to be placed on your internal DNC list must be honored indefinitely (no expiration) |
| **Cost** | First 5 area codes free per year; additional area codes are $72 each (as of 2025) |

#### Exemptions for Real Estate Agents

There are narrow exemptions, but they are frequently misunderstood:

**Existing Business Relationship (EBR) Exemption:**
- You may call someone on the DNC list if you have an existing business relationship with them
- An EBR exists if the consumer has made an inquiry or application within the past 3 months, OR has had a transaction with you within the past 18 months
- The 18-month clock starts from the date of the last transaction (e.g., closing date)
- The 3-month clock starts from the date of the last inquiry
- The EBR exemption is LOST immediately if the consumer asks to be placed on your internal DNC list, even if the relationship would otherwise qualify
- **Critical**: The EBR must be with YOUR brokerage, not with the individual consumer generally. A consumer who bought from a different brokerage does not have an EBR with you

**Personal Relationship Exemption:**
- Calls to people with whom you have a personal relationship (friends, family, acquaintances) are not considered telemarketing and are exempt
- This is informal and narrow --- do not stretch this to include casual contacts

**No Exemption for Cold Calling:**
- Real estate agents have NO special industry exemption from DNC rules
- Unlike some industries (charities, political campaigns, survey organizations), real estate is fully subject to all DNC rules
- Calling someone on the DNC list without an exemption is a violation, period

#### Penalties

| Violation Type | Penalty |
|---|---|
| **Per-call penalty** | Up to $51,744 per violation (adjusted for inflation, as of 2025) |
| **State enforcement** | State attorneys general can bring actions with additional penalties |
| **Private right of action** | Consumers can sue for $500 per violation, trebled to $1,500 for willful violations |
| **Pattern of violations** | Can result in FTC injunctive orders and business restrictions |

> **TheLeadEdge Impact**: Any phone outreach component of the system MUST integrate DNC scrubbing as a mandatory pre-call step. The system should block calls to DNC-listed numbers programmatically and log the scrub date for each record.

---

### 1.2 CAN-SPAM Act

The Controlling the Assault of Non-Solicited Pornography and Marketing Act (CAN-SPAM) governs all commercial email messages. It applies even to email sent to people with whom you have a relationship.

#### Key Requirements

| Requirement | Detail |
|---|---|
| **Accurate header info** | "From," "To," "Reply-To," and routing information must be accurate and identify the person or business initiating the message |
| **Non-deceptive subject lines** | Subject line must accurately reflect the content of the message |
| **Identify as advertisement** | Must clearly and conspicuously identify the message as an advertisement (if it is one) |
| **Physical address** | Must include a valid physical postal address of the sender. Can be a P.O. Box or registered commercial mail receiving agency address |
| **Opt-out mechanism** | Must include a clear, conspicuous, and functional opt-out mechanism |
| **Opt-out processing** | Must honor opt-out requests within 10 business days |
| **Opt-out mechanism validity** | The opt-out mechanism must be functional for at least 30 days after the message is sent |
| **No opt-out fee** | Cannot charge a fee, require personal information beyond an email address, or make the recipient take any step other than a reply email or visiting a single web page to opt out |
| **Third-party responsibility** | You cannot hire someone to send non-compliant email on your behalf --- you are responsible even if a vendor does the sending |

#### Transactional vs. Commercial Email

This distinction matters because **transactional emails are largely exempt** from CAN-SPAM requirements (except the prohibition on deceptive headers and subject lines):

| Type | Definition | CAN-SPAM Applies? |
|---|---|---|
| **Commercial** | Primary purpose is to promote a commercial product or service | Yes --- all requirements |
| **Transactional** | Facilitates an already agreed-upon transaction, provides warranty/safety info, or provides information about an ongoing business relationship | Partially --- only truthfulness requirements |
| **Mixed** | Contains both transactional and commercial content | Depends on the "primary purpose" --- if commercial content predominates, treat as commercial |

**Real estate examples:**
- "Here are 5 homes in your price range" to a buyer client = transactional (facilitating existing relationship)
- "I can help you sell your home for top dollar" to a cold lead = commercial
- Market update newsletters to non-clients = commercial
- CMA results sent to a listing client = transactional

#### Penalties

- Up to **$51,744 per email** in violation (adjusted for inflation)
- Criminal penalties possible for aggravated violations (spoofed headers, harvested addresses, dictionary attacks)
- State attorneys general can also enforce

> **TheLeadEdge Impact**: All automated email campaigns must include: physical address, unsubscribe link, advertisement identification. The system must process unsubscribes within 10 business days and maintain a suppression list.

---

### 1.3 TCPA (Telephone Consumer Protection Act)

The TCPA is the most aggressively enforced and litigated communications law in the United States. It applies to phone calls AND text messages and carries significant penalties. This is the single highest-risk regulation for real estate lead generation.

#### Core Restrictions

| Activity | Rule |
|---|---|
| **Autodialed calls to cell phones** | Prohibited without prior express consent |
| **Prerecorded/artificial voice calls to cell phones** | Prohibited without prior express written consent |
| **Autodialed calls to landlines** | Permitted (with DNC compliance) unless the call uses a prerecorded/artificial voice |
| **Prerecorded/artificial voice to landlines** | Prohibited without prior express consent |
| **Text messages to any phone** | Treated the same as a call --- texts to cell phones using an autodialer require prior express consent |
| **Marketing texts** | Require prior express written consent (higher standard) |
| **Time restrictions** | No calls before 8:00 AM or after 9:00 PM in the called party's local time |

#### Consent Standards

The TCPA has two distinct consent standards:

**Prior Express Consent (lower standard):**
- Required for non-marketing autodialed calls and prerecorded calls to cell phones
- Can be oral or written
- Must be given by the called party
- Can be revoked at any time by any reasonable means

**Prior Express Written Consent (higher standard):**
- Required for telemarketing/marketing calls or texts using an autodialer or prerecorded voice to cell phones
- Must be in writing (including electronic signatures, website forms, text message confirmations)
- Must clearly authorize the specific caller to make such calls/texts
- Must include the phone number to which calls can be made
- Must include a clear disclosure that the consumer is authorizing telemarketing calls and that consent is not a condition of purchase
- Cannot be obtained as a condition of purchasing any good or service

**What Counts as an "Autodialer" (ATDS):**
- After the Supreme Court's decision in *Facebook v. Duguid* (2021), an autodialer is equipment that uses a random or sequential number generator to either store or produce phone numbers to be called
- Manually dialing or using a system that calls from a pre-existing list (without random/sequential generation) is generally NOT auto-dialing under this narrower definition
- **However**: Many state TCPA equivalents (mini-TCPAs) have broader definitions. The FCC has also indicated it may interpret the definition more broadly in future rulemaking
- **Safe practice**: Treat any system that dials without manual human intervention as an autodialer

#### Revocation of Consent

- Consumers can revoke consent at any time through any reasonable means
- You must honor revocation requests within a reasonable time (the FCC has indicated this should be no more than 10 business days, with some proposing shorter windows)
- Revocation methods you must accept: spoken request during a call, text reply (STOP), email, written letter, or any other reasonable method
- You cannot require consumers to use a specific method to revoke consent

#### The "One-to-One" Consent Rule (Effective January 2025)

The FCC finalized a rule effective January 27, 2025, that tightens consent requirements:

- Consent must be given to **one specific seller at a time** (no more than one)
- "Comparison shopping" lead forms that share consent across multiple companies are no longer valid
- Consent must clearly and conspicuously identify the specific caller
- This has major implications for lead generation companies that sell leads to multiple agents

#### Penalties

| Violation Type | Penalty |
|---|---|
| **Statutory damages** | $500 per violation (per call or text) |
| **Willful/knowing violations** | Up to $1,500 per violation (treble damages) |
| **Class action exposure** | Extremely common --- TCPA class actions routinely settle for millions |
| **FCC enforcement** | Additional fines and penalties |

**Scale of risk**: A single campaign of 1,000 non-compliant texts could result in $500,000 to $1,500,000 in damages in a class action.

> **TheLeadEdge Impact**: Cold text messaging is effectively prohibited. Any text or autodialed phone campaigns require documented prior express written consent. The system must store consent records with timestamps, the specific language the consumer agreed to, and the phone number authorized. The system should NEVER text or auto-dial numbers without verified consent records.

---

### 1.4 Fair Housing Act

The Fair Housing Act (42 U.S.C. 3601-3619) applies to ALL real estate advertising and marketing, including lead generation targeting.

#### Protected Classes (Federal)

The Fair Housing Act prohibits discrimination based on seven protected classes:

1. **Race**
2. **Color**
3. **Religion**
4. **Sex** (including sexual orientation and gender identity per *Bostock v. Clayton County* and HUD's implementation)
5. **National origin**
6. **Familial status** (families with children under 18, pregnant women, people securing custody of children)
7. **Disability** (physical or mental)

Many states and localities add additional protected classes (see Section 2.3).

#### How It Applies to Lead Generation

| Activity | Compliance Requirement |
|---|---|
| **Geographic targeting** | Cannot draw targeting boundaries that exclude or target areas based on racial/ethnic composition ("redlining" or "reverse redlining") |
| **Demographic filtering** | Cannot filter leads by any protected class characteristic |
| **Ad targeting** | Cannot use Facebook/social media ad targeting that excludes protected classes (settled in *NFHA v. Facebook*, 2019) |
| **Language in marketing** | Cannot use words or phrases that indicate preference, limitation, or discrimination (e.g., "perfect for young professionals" excludes families; "ideal for Christian families" excludes other religions) |
| **Images in marketing** | Must reflect diversity; cannot use only images of one racial group if serving a diverse area |
| **Steering** | Cannot direct leads to or away from certain neighborhoods based on protected class characteristics |
| **Equal service** | Must provide the same level of service to all leads regardless of protected class |

#### Advertising Compliance

HUD's advertising guidelines prohibit specific words and phrases. A non-exhaustive list of risky terms:

| Avoid | Why | Safer Alternative |
|---|---|---|
| "Family-friendly neighborhood" | May discourage singles, elderly | "Great neighborhood" |
| "Walking distance to [specific church]" | Religious preference | "Walking distance to shops and services" |
| "Perfect for young couple" | Age/familial status | "Perfect starter home" |
| "Master bedroom" | Some brokerages dropping this term | "Primary bedroom" |
| "Exclusive community" | Can imply racial exclusion | "Private community" |
| "No children" (except 55+ communities) | Familial status | N/A --- cannot restrict |
| "Able-bodied" | Disability | N/A --- cannot require |

#### Digital Advertising Special Concerns

After the *NFHA v. Facebook* settlement and subsequent changes:
- Facebook/Meta removed the ability to target housing ads by age, gender, or zip code
- Housing ads on Facebook must use a "Special Ad Category" with restricted targeting
- Google Ads has similar housing ad restrictions
- Any digital lead generation campaign must comply with platform-specific housing ad restrictions
- **HUD has signaled increased scrutiny** of algorithmic targeting that produces discriminatory outcomes, even if no discriminatory intent exists

#### Penalties

| Type | Penalty |
|---|---|
| **Administrative complaints (HUD)** | Up to $21,039 for first offense; up to $52,596 for second offense within 5 years; up to $105,194 for third+ |
| **Federal court action** | Unlimited compensatory and punitive damages |
| **Pattern/practice cases (DOJ)** | Up to $105,194 for first offense; $210,389 for subsequent |
| **License implications** | State real estate commissions can suspend or revoke license for Fair Housing violations |
| **Reputation damage** | Fair Housing complaints are public and can be devastating to a real estate business |

> **TheLeadEdge Impact**: Lead scoring and targeting algorithms must never use protected class characteristics as inputs. Geographic targeting must be based on legitimate market criteria (price range, property type, school district quality) not demographic composition. All marketing templates must be reviewed for Fair Housing compliance before use.

---

### 1.5 FCRA (Fair Credit Reporting Act)

The FCRA regulates the use of consumer credit information and "consumer reports" for marketing purposes.

#### How It Applies to Real Estate Lead Generation

| Scenario | FCRA Applies? | Notes |
|---|---|---|
| **Using credit scores to target leads** | Yes | Cannot access or use credit reports for marketing without a permissible purpose |
| **Pre-foreclosure data from public records** | No | Public records (NODs, lis pendens) are not consumer reports |
| **Tax delinquency data from public records** | No | Public tax records are not consumer reports |
| **Purchased marketing lists based on credit data** | Possibly | If the list provider used credit data to compile the list, the list itself may be a consumer report |
| **Firm offers of credit or insurance** | Yes | If you are making a "firm offer" based on credit criteria, FCRA prescreened offer rules apply |
| **Mortgage data from public records** | No | Recorded mortgages are public records |

#### Key Rules

- **Permissible purpose required**: You can only pull a consumer report for a permissible purpose (credit transaction, employment, insurance, legitimate business need related to a transaction initiated by the consumer, etc.)
- **Marketing is NOT a permissible purpose**: You cannot pull credit reports to identify marketing targets
- **Prescreened offers**: You CAN use prescreened lists from credit bureaus to make "firm offers of credit or insurance" --- but this applies to lenders, not real estate agents
- **Adverse action notices**: If you take adverse action (deny service) based on information in a consumer report, you must provide an adverse action notice

#### Safe Practice for TheLeadEdge

- **DO** use public records (tax records, court filings, property records) for lead generation --- these are not consumer reports
- **DO NOT** purchase lists that are compiled based on credit bureau data for marketing purposes
- **DO NOT** access credit reports to identify or prioritize leads
- **ASK list providers** whether their data includes any credit bureau-sourced information
- If using a data aggregator like ATTOM, PropStream, or ListSource, their terms of service should specify whether any credit data is included and restrict its use accordingly

> **TheLeadEdge Impact**: The system should never integrate credit bureau data. All lead sources should be verified as non-FCRA-regulated (public records, MLS data, self-reported information). Document the data source for every lead record.

---

### 1.6 RESPA (Real Estate Settlement Procedures Act)

While RESPA primarily governs settlement services, it has implications for lead generation referral arrangements.

#### Key Provisions Affecting Lead Generation

| Rule | Detail |
|---|---|
| **Section 8(a) --- Kickback prohibition** | Prohibits giving or receiving anything of value for referrals of settlement service business |
| **Section 8(b) --- Fee splitting** | Prohibits fee splits or unearned fees for settlement services |
| **Section 8(c) --- Exceptions** | Payments for goods or services actually furnished are permitted at fair market value |

#### What This Means for Lead Generation

- You **cannot** pay an unlicensed person a referral fee for sending you buyer or seller leads (in most states --- some states allow limited referral fees to unlicensed parties under specific conditions)
- You **can** pay for advertising and marketing services at fair market value (paying for leads from a lead gen company is generally permissible if structured as a marketing service fee, not a referral fee tied to a transaction)
- You **can** pay referral fees to other licensed agents/brokers
- You **cannot** receive kickbacks from settlement service providers (title companies, lenders, home inspectors) for referring business to them
- **Affiliated business arrangements** (AfBAs) are permitted with proper disclosure using the Affiliated Business Arrangement Disclosure Statement

> **TheLeadEdge Impact**: If the system ever evolves to include referral tracking or partnerships with service providers, RESPA compliance must be built in. Referral fee structures must be reviewed by legal counsel.

---

## 2. State-Specific Regulations

### 2.1 Foreclosure Solicitation Restrictions

Many states have enacted laws specifically restricting solicitation of homeowners in foreclosure. These are among the most restrictive and heavily penalized regulations affecting real estate lead generation. The following covers the most restrictive states.

#### Top 10 Most Restrictive States

**1. California**
- **Statute**: Cal. Civ. Code 1695 et seq. (Home Equity Sales Contract Act)
- **Cooling period**: Cannot contact homeowner until 5 business days after the Notice of Default (NOD) is recorded
- **Required disclosures**: Must provide a specific statutory notice informing the homeowner of their rights
- **Contract restrictions**: Any purchase contract for a home in foreclosure must include a 5-day right of rescission
- **Registration**: Foreclosure consultants must register with the state DOJ and post a $100,000 surety bond
- **Prohibited practices**: Cannot charge upfront fees for foreclosure consulting services; cannot take any interest in the property until the contract period expires
- **Penalties**: Violation is a criminal offense (public offense); contracts are voidable; civil penalties; license revocation
- **Notes**: One of the broadest definitions of "foreclosure consultant" --- can capture real estate agents who provide certain advice

**2. New York**
- **Statute**: NY Real Property Law 265-a; NY Gen. Bus. Law Art. 29-H (Distressed Property Consultant Law)
- **Cooling period**: Must wait until the foreclosure action is filed AND the homeowner has been served
- **Required disclosures**: Must provide a "Consumer Bill of Rights" notice
- **Registration**: Distressed property consultants must register with the NYS Department of State
- **Contract restrictions**: 5-day right of rescission on all contracts; contracts must be in writing and in the homeowner's primary language if negotiated in a language other than English
- **Prohibited practices**: Cannot receive compensation until services are fully performed; cannot take power of attorney
- **Penalties**: Violation is a Class E felony; contracts are void; civil damages of actual damages or $1,000, whichever is greater

**3. Illinois**
- **Statute**: 765 ILCS 940 (Distressed Property Protection Act)
- **Required disclosures**: Must provide specific statutory notice before entering into any agreement
- **Contract restrictions**: 14-day right of rescission (one of the longest in the country)
- **Prohibited practices**: Cannot acquire interest in property for less than 82% of fair market value; cannot charge fees exceeding 8% of the home's value
- **Penalties**: Violation is a Class B misdemeanor; contracts are voidable; civil penalties

**4. Maryland**
- **Statute**: MD Real Property Code 7-301 et seq. (Protection of Homeowners in Foreclosure Act)
- **Registration**: Foreclosure consultants must register with the Commissioner of Financial Regulation and post a $50,000 surety bond
- **Cooling period**: Cannot solicit until at least 10 days after the foreclosure filing
- **Required disclosures**: Must provide a specific disclosure form in 14-point bold type
- **Contract restrictions**: 5-day right of rescission
- **Prohibited practices**: Cannot collect fees until services are fully rendered
- **Penalties**: Misdemeanor; fines up to $10,000 and/or imprisonment up to 1 year; civil penalties

**5. Massachusetts**
- **Statute**: M.G.L. c. 244 35A-35D (Predatory Home Equity Practices Act) and c. 93A
- **Required disclosures**: Must provide notice that the homeowner has the right to cancel any agreement within 5 business days
- **Prohibited practices**: Cannot charge upfront fees; cannot acquire the property for less than 70% of fair market value (one of the strictest thresholds)
- **Penalties**: Criminal penalties; void contracts; unfair trade practice violations under 93A (treble damages and attorney fees)

**6. Minnesota**
- **Statute**: Minn. Stat. 325N (Equity Stripping and Home Foreclosure Prevention Act)
- **Registration**: Foreclosure reconveyance purchasers must register with the state
- **Contract restrictions**: 5-day right of rescission; contract must include an independent appraisal
- **Prohibited practices**: Cannot purchase property for less than 90% of appraised value (strictest threshold in the nation)
- **Penalties**: Misdemeanor; void contracts; civil damages

**7. New Jersey**
- **Statute**: N.J.S.A. 46:10B-51 (New Jersey Foreclosure Act)
- **Cooling period**: Cannot send direct mail to homeowners in foreclosure until at least 30 days after the lis pendens is filed
- **Required disclosures**: Any solicitation must include a specific disclaimer in 12-point type
- **Direct mail content**: Must include specific language identifying the sender as a licensed real estate professional
- **Penalties**: Civil penalties; license sanctions

**8. Georgia**
- **Statute**: O.C.G.A. 10-1-393.6 (Foreclosure Rescue Fraud Act)
- **Required disclosures**: Must provide specific written disclosures before any agreement
- **Contract restrictions**: 3-day right of rescission
- **Prohibited practices**: Cannot charge upfront fees; cannot take power of attorney; cannot induce homeowner to sign documents transferring interest
- **Penalties**: Unfair trade practice violation; felony for pattern violations

**9. Washington**
- **Statute**: RCW 61.34 (Distressed Property Conveyance Act)
- **Required disclosures**: Must provide statutory warning in 14-point bold type
- **Contract restrictions**: 5-day right of rescission; independent appraisal required
- **Prohibited practices**: Cannot purchase for less than 82% of fair market value; cannot charge consulting fees exceeding 8%
- **Penalties**: Class B felony for pattern violations; void contracts; civil damages

**10. Connecticut**
- **Statute**: Conn. Gen. Stat. 36a-489cc et seq. (Foreclosure Consultant Act)
- **Registration**: Foreclosure consultants must register with the Department of Banking
- **Required disclosures**: Must provide a specific Consumer Notice before any services
- **Contract restrictions**: 3-business-day right of rescission
- **Prohibited practices**: Cannot collect fees until services are completed; cannot take power of attorney
- **Penalties**: Criminal penalties; void contracts; private right of action for damages

#### General Best Practices for Foreclosure Solicitation

Regardless of state:

1. **Wait**: Never contact a homeowner in the first 30 days after a foreclosure filing (even if the state allows earlier contact, it is ethically and practically better to wait)
2. **Identify yourself**: Always clearly state that you are a licensed real estate agent, not a government agency or foreclosure rescue company
3. **No exterior references**: Never reference "foreclosure," "default," or "delinquency" on the outside of any mail piece (envelope, postcard)
4. **No pressure**: Do not create false urgency beyond what legitimately exists
5. **Know your state**: Before doing ANY pre-foreclosure outreach, research your specific state's requirements in detail

---

### 2.2 State Do Not Call Lists

Many states maintain their own Do Not Call registries with rules that are stricter than the federal registry.

#### Key Differences from the Federal DNC

| Feature | Federal DNC | Common State DNC Variations |
|---|---|---|
| **EBR exemption** | 18 months (transaction) / 3 months (inquiry) | Many states shorten or eliminate the EBR exemption (e.g., Indiana: no EBR exemption) |
| **Update frequency** | Must scrub every 31 days | Some states require more frequent updates |
| **Registration** | Free for first 5 area codes | Some states require separate telemarketer registration (fee varies) |
| **Penalties** | Up to $51,744 per call | State penalties can be additional and separate |
| **Scope** | Interstate and intrastate calls | Applies to intrastate calls; some have different rules for in-state vs. out-of-state callers |

#### States with Notable DNC Variations

| State | Key Difference |
|---|---|
| **Indiana** | No EBR exemption --- even existing clients cannot be called if on the state DNC list without specific consent |
| **Pennsylvania** | Requires telemarketers to register and pay an annual fee; steeper penalties |
| **Texas** | Maintains a separate state DNC list; requires registration for commercial telemarketers |
| **Florida** | Separate state DNC list; allows private right of action with $500/violation |
| **Colorado** | Separate state DNC list; requires telemarketers to register with the Public Utilities Commission |
| **Missouri** | Maintains a no-call list; attorney general actively enforces |
| **Louisiana** | State DNC list with separate registration; no EBR exemption for some categories |
| **Oregon** | Telephonic Sellers Registration (TSR) required; strong enforcement |
| **Wyoming** | Separate no-call list with strict penalties |
| **Wisconsin** | No-call list maintained by DATCP; broad definition of telemarketing |

#### Compliance Approach

- **Always scrub against BOTH** the federal and state DNC lists for any state you are calling into
- Research your specific state's registration requirements for telemarketers
- When in doubt, treat the strictest rule as the one that applies
- Some states require you to register as a telemarketer even if you are a real estate agent making calls --- check your state's definition of "telemarketer"

---

### 2.3 State Real Estate Commission Rules

State real estate commissions impose their own marketing and solicitation rules beyond federal law.

#### Common State Commission Requirements

| Requirement | Detail |
|---|---|
| **Licensee identification** | Most states require all advertising and solicitation to identify the licensee and their brokerage by name |
| **Broker supervision** | Many states require broker approval of marketing materials before use |
| **Team name rules** | Many states regulate how team names can be used in advertising (must not be misleading, must include brokerage name) |
| **Advertising approval** | Some states require pre-approval of advertising by the broker, with documentation retained |
| **License number display** | Some states (e.g., California DRE) require the license number on all solicitation materials |
| **"Realtor" usage** | Use of "REALTOR" requires NAR membership; it is a registered trademark and must be used properly (capitalized, with the registered trademark symbol on first use) |

#### Additional State Protected Classes

Many states add protected classes beyond the federal seven. Examples:

| State | Additional Protected Classes |
|---|---|
| **California** | Ancestry, marital status, source of income, sexual orientation, gender identity, genetic information, primary language, immigration status, military/veteran status |
| **New York** | Age, marital status, sexual orientation, gender identity, military status, source of income, domestic violence victim status |
| **Illinois** | Ancestry, age, marital status, order of protection status, military status, sexual orientation, unfavorable military discharge |
| **Washington** | Marital status, sexual orientation, gender identity, veteran/military status, use of a trained guide dog |
| **Colorado** | Marital status, ancestry, creed, sexual orientation, source of income |
| **Massachusetts** | Age, ancestry, marital status, sexual orientation, gender identity, military/veteran status, source of income, genetic information |
| **Oregon** | Marital status, source of income, sexual orientation, gender identity |
| **New Jersey** | Marital status, ancestry, affectional/sexual orientation, gender identity, source of lawful income, nationality |
| **Minnesota** | Marital status, public assistance status, sexual orientation, gender identity |
| **Maryland** | Marital status, sexual orientation, gender identity, source of income |

> **TheLeadEdge Impact**: Lead scoring and targeting must also avoid using any state-level protected class as a factor. The system should be reviewed for compliance with the specific state(s) where it will be deployed.

---

### 2.4 Local Anti-Solicitation Ordinances

Many cities and counties have their own solicitation ordinances that add requirements beyond state and federal law.

#### Common Local Restrictions

| Restriction Type | Detail |
|---|---|
| **Solicitor registration** | Many cities require door-to-door solicitors to register and obtain a permit (fee varies, typically $25--$100) |
| **No-solicitation sign enforcement** | Many cities have ordinances that make ignoring a "No Solicitation" sign a violation (fine varies) |
| **Time restrictions** | Local ordinances often restrict door-knocking hours more narrowly than state law (e.g., 9 AM -- 6 PM vs. 8 AM -- 9 PM) |
| **HOA restrictions** | Many HOAs prohibit or restrict door-to-door solicitation within the community --- these are contractual, not legal, but violating them can create problems with potential clients |
| **Specific neighborhood restrictions** | Some cities allow neighborhoods to register as "no solicitation" zones |

#### How to Check

1. Search "[city name] solicitation ordinance" or "[city name] peddler solicitor ordinance"
2. Check the city clerk or business licensing office website
3. Contact the local police non-emergency line for door-knocking rules
4. Check with the HOA management company for any community-specific restrictions

---

## 3. Compliance by Outreach Method

### 3.1 Direct Mail

Direct mail is the **lowest-risk outreach channel** for real estate lead generation. However, it still has compliance requirements.

#### Federal Requirements

| Requirement | Detail |
|---|---|
| **Return address** | Must include a valid return address (USPS requirement for First-Class and Marketing Mail) |
| **Truthful content** | Cannot make false or misleading claims about your services |
| **Fair Housing compliance** | Content, images, and targeting must comply with Fair Housing Act |
| **No exterior distress references** | Do not reference "foreclosure," "default," "delinquency," "probate," "divorce," or other distressing situations on the exterior of envelopes or on postcards (visible content) |

#### State-Specific Requirements

| State | Additional Requirements |
|---|---|
| **California** | Must include your CalDRE license number on marketing materials |
| **New Jersey** | Pre-foreclosure mail must include a specific disclaimer in 12-point type and cannot be sent until 30 days after lis pendens filing |
| **New York** | Distressed property solicitations must include a "Consumer Bill of Rights" notice |
| **Many states** | Must identify yourself as a licensed real estate agent/broker in all mail |

#### Best Practices

- Use envelopes (not postcards) for sensitive lead types (pre-foreclosure, probate, divorce) to keep the message private
- Always include your full name, brokerage name, and license number (if state-required)
- Include a clear way for the recipient to opt out of future mailings
- Track all mail pieces sent with dates and addresses for compliance records
- Do not use government-style envelopes or formatting that could be mistaken for official government correspondence
- Maintain a suppression list of recipients who have opted out

---

### 3.2 Phone Calls

Phone outreach carries **moderate to high legal risk** depending on compliance practices.

#### Compliance Requirements Summary

| Requirement | Detail |
|---|---|
| **DNC scrubbing** | Scrub against federal and state DNC lists every 31 days |
| **Internal DNC list** | Maintain and honor your own DNC list |
| **Time restrictions** | No calls before 8:00 AM or after 9:00 PM in the recipient's local time (stricter in some states) |
| **Caller ID** | Must transmit accurate caller ID information (FCC rule) |
| **Identification** | Must identify yourself, your brokerage, and the purpose of the call within the first 30 seconds |
| **TCPA compliance** | Manual dialing to cell phones is permitted; auto-dialing or prerecorded messages require prior express consent |
| **Recording consent** | Comply with call recording laws (one-party vs. two-party consent states --- see below) |

#### Call Recording Consent by State

In the United States, call recording laws fall into two categories:

**One-Party Consent States** (only one party to the call needs to consent --- if you are recording your own call, your consent is sufficient):
Alabama, Alaska, Arizona, Arkansas, Colorado, District of Columbia, Georgia, Hawaii, Idaho, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, Michigan (with exceptions), Minnesota, Mississippi, Missouri, Nebraska, Nevada (case law is mixed --- treat as two-party to be safe), New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon (with exceptions for in-person conversations), Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, West Virginia, Wisconsin, Wyoming

**Two-Party (All-Party) Consent States** (all parties must consent to the recording):
California, Connecticut, Delaware, Florida, Illinois, Maryland, Massachusetts, Michigan (when there is an expectation of privacy), Montana, New Hampshire, Oregon (for in-person), Pennsylvania, Washington

**If calling across state lines**: The safest practice is to apply the stricter two-party consent standard. If you are in a one-party state but calling into a two-party state, follow the two-party state's rules.

**How to comply with two-party consent**: Begin every call with a disclosure: "This call may be recorded for quality and training purposes. Do you consent to being recorded?" If they decline, turn off recording.

#### State-Specific Time Restrictions

Some states restrict calling hours more narrowly than the federal 8 AM -- 9 PM window:

| State | Calling Hours |
|---|---|
| **Massachusetts** | 8 AM -- 8 PM (one hour shorter in the evening) |
| **Oregon** | 9 AM -- 8 PM |
| **Various cities** | Some municipalities restrict commercial calls further --- check local ordinances |

---

### 3.3 Email

Email carries **moderate legal risk** and is governed primarily by the CAN-SPAM Act.

#### Compliance Requirements

| Requirement | Detail |
|---|---|
| **Opt-in** | CAN-SPAM does NOT require opt-in for commercial email (unlike GDPR) --- you CAN send unsolicited commercial email if you comply with all other requirements |
| **Physical address** | Must include a valid physical postal address |
| **Unsubscribe mechanism** | Must include a clear, functional unsubscribe link or mechanism |
| **Unsubscribe processing** | Must process opt-outs within 10 business days |
| **Accurate headers** | From name, email address, and subject line must be truthful |
| **Ad identification** | Must clearly identify the message as an advertisement |
| **No harvested addresses** | Cannot use automated tools to harvest email addresses from websites |

#### California-Specific Email Rules

California Business & Professions Code Section 17529.5 adds state-level requirements:
- Prohibits email with falsified header information
- Prohibits email with deceptive subject lines
- Private right of action for recipients (up to $1,000 per email, capped at $1,000,000 per campaign)

#### Best Practices for Real Estate Email Marketing

1. **Use a reputable email service provider** (Mailchimp, Constant Contact, SendGrid) that enforces CAN-SPAM compliance
2. **Include your brokerage name, your name, and license number** (where required by state)
3. **Honor unsubscribes immediately** --- even though the law gives you 10 days, best practice is real-time processing
4. **Do not buy email lists** from unverified sources --- list quality directly affects your deliverability and legal risk
5. **Keep records** of where you obtained each email address and when
6. **Separate transactional and commercial emails** --- do not add marketing content to transactional emails if you want to maintain the transactional exemption

---

### 3.4 Text / SMS

Text messaging carries the **highest legal risk** of any outreach method for real estate lead generation.

#### Compliance Requirements

| Requirement | Detail |
|---|---|
| **Prior express written consent** | Required for ALL marketing texts. Consent must be documented with the consumer's signature (electronic signature acceptable) |
| **Clear identification** | Must identify yourself and your business in every text |
| **Opt-out mechanism** | Must support "STOP" keyword to opt out, and honor it immediately |
| **No auto-texting without consent** | Using any automated system to send texts to cell phones without prior express written consent violates the TCPA |
| **One-to-one consent** | Under the FCC's 2025 rule, consent must be specific to your business (not a lead form shared with multiple companies) |
| **Time restrictions** | Same as phone calls --- no texts before 8 AM or after 9 PM in the recipient's local time |
| **Content requirements** | Must include your business name and a way to opt out in every message |

#### When Texting Is Permissible

| Scenario | Permissible? | Notes |
|---|---|---|
| Texting a current client about their transaction | Yes | Transactional, and you have implied consent from the existing relationship |
| Texting a past client with a market update | Risky | Only if you obtained prior express written consent for marketing texts |
| Cold texting a pre-foreclosure homeowner | **No** | No prior consent exists; this is a TCPA violation |
| Texting someone who filled out a web form and checked a consent box | Yes | If the consent language was clear, conspicuous, and specific to your business |
| Texting a FSBO who posted their number publicly | **No** | Posting a phone number publicly does not constitute consent to receive marketing texts |

#### Best Practice: Avoid Cold Texting Entirely

Given the legal landscape, the recommendation for TheLeadEdge is clear:

- **Do not cold text** any lead under any circumstances
- **Do text** only people who have provided documented prior express written consent
- If using a texting platform, ensure it stores consent records and supports STOP keyword processing
- If a lead opts in via web form, the form must include specific consent language naming your business and clearly stating the consumer agrees to receive marketing text messages

---

### 3.5 Door Knocking

Door knocking carries **low legal risk** but has practical and local compliance considerations.

#### Legal Framework

| Requirement | Detail |
|---|---|
| **First Amendment protection** | Door-to-door solicitation has First Amendment protection (the Supreme Court struck down blanket bans in *Watchtower Bible & Tract Society v. Village of Stratton*, 2002) |
| **No-solicitation signs** | In most jurisdictions, ignoring a "No Solicitation" sign is a violation of local ordinance. However, some courts have held that real estate agents providing market information (not selling a product) are not "soliciting" |
| **Local permits** | Some municipalities require a solicitor's permit. Check before knocking |
| **Time restrictions** | Follow local ordinances; absent a local rule, the general guideline is 9 AM to 7 PM (or sunset, whichever is earlier) |
| **Trespassing** | If asked to leave, you must leave immediately. Returning after being told to leave is trespassing |
| **Identification** | Always carry your real estate license and a business card. Some municipalities require visible ID/badge |

#### Best Practices

1. **Respect "No Solicitation" signs** --- even if you believe you have a legal right to knock, it is not worth the conflict
2. **Have a clear purpose** --- "I just sold a home in your neighborhood" is educational, not solicitation in many jurisdictions
3. **Leave material, not pressure** --- if no one is home, leave a door hanger or card (never leave anything in a mailbox --- that is a federal offense, as mailboxes are for USPS use only)
4. **Never open gates, fences, or doors** --- stay on the public path
5. **Be aware of Ring doorbells and security cameras** --- your conduct is likely being recorded
6. **Track where you have been** --- maintain a log for compliance purposes

---

### 3.6 Social Media

Social media marketing has **unique compliance challenges** due to platform terms of service and evolving advertising regulations.

#### Platform-Specific Housing Ad Rules

| Platform | Rules |
|---|---|
| **Facebook/Meta** | Housing ads must use "Special Ad Category"; cannot target by age, gender, zip code, or other protected characteristics; limited geographic targeting (minimum 15-mile radius) |
| **Instagram** | Same as Facebook (same platform) |
| **Google Ads** | Personalized housing ads cannot use age, gender, parental status, marital status, or zip code targeting |
| **LinkedIn** | Follows general anti-discrimination rules; housing-specific restrictions less formalized but still apply |
| **TikTok** | Housing ads subject to anti-discrimination requirements |

#### FTC Disclosure Requirements

If you receive any form of compensation for promoting a product or service on social media, you must disclose it:

| Scenario | Disclosure Required? | How |
|---|---|---|
| Posting about a listing you represent | Yes --- you are the agent | Identify yourself as the listing agent |
| Sharing a post from a lender partner | Yes --- if there is a referral relationship | Use #ad or #sponsored |
| Paying for a sponsored post | Yes | Platform ad labels usually satisfy this |
| Organic posts about your services | Identify yourself as an agent | Include your brokerage name and license number (if state-required) |

#### Social Media Compliance Checklist

- [ ] All housing ads use the platform's "Special Ad Category" (where applicable)
- [ ] No targeting by protected class characteristics
- [ ] Agent and brokerage clearly identified in profile and posts
- [ ] License number displayed where required by state
- [ ] All testimonials include appropriate disclaimers
- [ ] No guaranteed outcome claims ("I will sell your home in 30 days")
- [ ] Comments and DMs handled consistently to avoid steering or discrimination claims
- [ ] All paid partnerships properly disclosed

---

## 4. Compliance by Lead Source

### 4.1 Pre-Foreclosure Leads

Pre-foreclosure leads are the **most heavily regulated** lead source in real estate.

#### Compliance Matrix by State Type

| Regulation | What to Do |
|---|---|
| **State foreclosure solicitation laws** | Research your specific state BEFORE any outreach (see Section 2.1) |
| **Waiting periods** | Honor all state-mandated cooling periods. Even where not required, wait at least 30 days after filing |
| **Required disclosures** | Include all state-required disclosures in mail and verbal communications |
| **No exterior references** | Never mention "foreclosure," "default," or "delinquency" on envelope exterior or postcard |
| **Licensing identification** | Always identify yourself as a licensed real estate agent (not a "foreclosure specialist," "loss mitigation expert," or "government program representative") |
| **Fair value requirement** | Some states require that you not acquire the property for less than a specified percentage of fair market value (70--90% depending on state) |
| **Right of rescission** | Many states mandate a 3--14 day right of rescission on any contract with a homeowner in foreclosure |
| **Bond/registration** | Some states require foreclosure consultants to register and post a surety bond |

#### Safe Outreach Template Elements

Every pre-foreclosure outreach should include:
1. Your full legal name and license number
2. Your brokerage name and address
3. A statement that you are a licensed real estate agent
4. No implication of government affiliation
5. No use of the word "foreclosure" on the exterior of mailings
6. The homeowner's right to consult with an attorney
7. Any state-required specific disclosures
8. Your contact information and a way to opt out

---

### 4.2 Probate Leads

Probate leads involve contacting personal representatives (executors/administrators) of deceased persons' estates. While not as heavily regulated as pre-foreclosure, ethical and sensitivity requirements are significant.

#### Legal Considerations

| Issue | Detail |
|---|---|
| **Public records** | Probate filings are public records and can be accessed legally |
| **Who to contact** | Contact the personal representative (executor/administrator), NOT the deceased or surviving family members who are not involved in the estate |
| **Timing** | No federal or most state laws mandate a waiting period, but ethical best practice is to wait at least 30--60 days after the probate filing |
| **Content** | Never be salesy or aggressive. The representative is often grieving. Lead with empathy and offer to help with the real estate aspect of estate settlement |
| **Attorney involvement** | Many probate sales require court approval. Be prepared to work with estate attorneys |
| **Court-ordered sales** | Some jurisdictions require probate property to be listed at appraised value or sold through a specific court process |

#### State-Specific Probate Rules

| State | Key Rules |
|---|---|
| **California** | Probate sales often require court confirmation; overbid process at court hearing; IAEA (Independent Administration of Estates Act) allows some sales without court confirmation |
| **New York** | Surrogate's Court handles probate; executor has broad authority for real property sales in many cases |
| **Florida** | Summary administration available for smaller estates; personal representative can sell without court approval in many cases |
| **Texas** | Independent administration (most common) allows executor to sell without court approval; dependent administration requires court order |

#### Ethical Best Practices

1. Wait at least 30--60 days after probate filing before initial outreach
2. Use empathetic, service-oriented language ("I help families navigate the real estate aspects of estate settlement")
3. Never pressure for a quick sale
4. Acknowledge the loss and the difficulty of the situation
5. Offer a free CMA or home valuation with no obligation
6. Be prepared to coordinate with estate attorneys and other professionals

---

### 4.3 Divorce Leads

Divorce leads involve contacting parties to a dissolution of marriage where real property may need to be sold.

#### Legal Considerations

| Issue | Detail |
|---|---|
| **Public records** | Divorce filings are generally public records, though some jurisdictions seal financial details |
| **Who to contact** | Contact either party individually; do NOT contact both parties simultaneously or reveal that you have contacted the other party |
| **Timing** | No mandatory waiting period in most states, but ethical best practice is to wait until after the initial filing period (typically 30+ days) |
| **Dual agency risk** | If both parties contact you separately, you may face a dual agency situation. Disclose immediately and consider referring one party to another agent |
| **Court orders** | Some divorces involve court orders regarding property disposition. Do not interfere with or contradict court orders |
| **Restraining orders** | Be aware that many divorce filings include automatic temporary restraining orders on property disposition. Do not encourage any party to violate court orders |

#### Ethical Best Practices

1. Use extremely sensitive, non-judgmental language
2. Frame your outreach around helping with a transition, not capitalizing on a difficult situation
3. Never mention "divorce" on the exterior of any mailing
4. Be aware that one party may not want the home sold --- you cannot take sides
5. Have referral relationships with divorce attorneys and financial advisors
6. Consider waiting until the property is explicitly listed in the divorce proceedings before outreach

---

### 4.4 Expired & FSBO Leads

Expired listings and For Sale By Owner (FSBO) properties are common lead sources that involve MLS data usage concerns.

#### MLS Data Usage Rules

| Rule | Detail |
|---|---|
| **Expired listings** | Contact information from expired listings in the MLS may be used for solicitation ONLY if your MLS rules permit it. Many MLSs have specific rules about soliciting expired listings |
| **Withdrawn listings** | Similar rules as expired --- check your MLS |
| **Timing** | Most MLSs allow contact on the day the listing expires. Some prohibit contact during a "pending" period |
| **FSBO from MLS** | FSBO data in the MLS (if your MLS includes it) is subject to MLS data usage rules |
| **FSBO from public sources** | FSBO signs, Craigslist postings, and other public advertisements are NOT MLS data and can be used freely |

#### DNC Considerations for Expired/FSBO

- An expired listing seller who listed their home for sale and provided their phone number to the MLS does NOT create an EBR with you (unless they were your client)
- A FSBO who posts their phone number publicly is not consenting to telemarketing --- they are inviting inquiries about their property from potential buyers, not from agents
- **Best practice**: Scrub all phone numbers against the DNC registry before calling, regardless of how you obtained the number

---

### 4.5 Public Records Generally

#### FOIA and Public Access Rights

| Principle | Detail |
|---|---|
| **Federal FOIA** | The Freedom of Information Act applies to federal agencies, not state/local records |
| **State open records laws** | Every state has its own public records/open records law (e.g., California Public Records Act, Texas Public Information Act, New York FOIL) |
| **County recorder records** | Property records, deeds, mortgages, liens, and NODs are public in all states |
| **Court records** | Most court filings (probate, divorce, civil) are public, though some may be sealed |
| **Tax records** | Property tax assessments and delinquency records are public |
| **Building permits** | Building permit applications and inspections are public records in virtually all jurisdictions |

#### Commercial Use Limitations

While the records themselves are public, there are some limitations on commercial use:

| Limitation | Detail |
|---|---|
| **Bulk data sales** | Some jurisdictions restrict bulk commercial data sales from public records (e.g., limiting how much data can be downloaded at once) |
| **Driver's license data** | The Driver's Privacy Protection Act (DPPA) restricts commercial use of motor vehicle records |
| **Voter registration data** | Many states restrict commercial use of voter registration data |
| **Purpose restrictions** | Some states limit the use of public records data to specific purposes and prohibit purely commercial solicitation purposes |
| **Court record use** | While accessible, using court records (bankruptcy, divorce) for unsolicited commercial solicitation may raise ethical concerns even if not legally prohibited |

#### Best Practices

1. Always obtain data through official channels (county websites, FOIA requests) or reputable data providers
2. Document the source of every lead record
3. Do not scrape government websites if their terms of use prohibit it
4. Respect any volume limitations on bulk data requests
5. When in doubt about commercial use rights, submit a formal public records request and let the agency determine what can be released

---

## 5. MLS Terms of Service Compliance

### 5.1 Data Usage Restrictions

MLS data is licensed data, not public data. It is subject to the terms of service of your specific MLS, which are generally consistent in their core restrictions but vary in details.

#### Universal MLS Data Rules

| Rule | Detail |
|---|---|
| **Licensed use only** | MLS data can only be used by licensed participants and subscribers in the course of their real estate business |
| **No resale** | MLS data cannot be sold, sublicensed, or provided to third parties for commercial purposes |
| **No non-real-estate use** | Data cannot be used for purposes unrelated to real estate transactions (no using MLS data to market other products/services) |
| **Accuracy obligation** | Agents have an obligation to ensure MLS data they use or display is accurate and current |
| **Confidential fields** | Some MLS fields are confidential (e.g., seller motivation, showing instructions, lockbox codes, commission rates) and cannot be shared outside the MLS |
| **Data security** | Must protect MLS data from unauthorized access; cannot store it in unsecured systems |

### 5.2 IDX vs. VOW vs. Personal Use

| Data Type | Description | Usage Restrictions |
|---|---|---|
| **IDX (Internet Data Exchange)** | Active listing data displayed on agent/broker websites | Must display data with required disclaimers; cannot alter or misrepresent; must include listing broker attribution; cannot use to solicit listing agents' clients directly |
| **VOW (Virtual Office Website)** | Broader data set (including sold data) displayed to registered users | Users must register and agree to terms; cannot display data to unregistered public; additional restrictions on data mining |
| **Personal use** | Data accessed through the MLS system for your own business | Most flexible use; still cannot resell or use for non-real-estate purposes |
| **Sold data** | Closed transaction records | Usage restrictions vary by MLS; many restrict display to registered users only; cannot use to solicit sellers of competing properties |

### 5.3 Data Storage and Retention

| Rule | Detail |
|---|---|
| **Active listing data** | Can generally be stored as long as the listing is active; must be updated or removed when the listing status changes |
| **Sold data** | Some MLSs restrict how long sold data can be retained locally (commonly 1--3 years) |
| **Expired listing data** | Must be removed or updated within the timeframe specified by your MLS (commonly 24--48 hours after expiration) |
| **Client portal data** | Data displayed on your website must be refreshed at least as frequently as your MLS requires (commonly every 12--24 hours) |
| **Backup/archive** | Some MLSs prohibit creating offline archives of MLS data |
| **Data upon termination** | If you leave the MLS or your license is suspended, you must delete all MLS data in your possession |

### 5.4 Penalties for MLS Violations

| Penalty | Detail |
|---|---|
| **Warning/letter** | First offense for minor violations |
| **Fines** | Vary by MLS; commonly $500--$15,000 per violation |
| **Suspension** | Temporary suspension of MLS access (commonly 30--90 days for serious violations) |
| **Termination** | Permanent expulsion from the MLS for severe or repeated violations |
| **NAR ethics complaint** | If the agent is a REALTOR, an ethics complaint can be filed with the local association |
| **Reporting to state commission** | Severe violations may be reported to the state real estate commission, which can affect your license |

### 5.5 TheLeadEdge-Specific MLS Compliance

For the TheLeadEdge system specifically:

| Activity | Compliance Status | Notes |
|---|---|---|
| Analyzing MLS data to identify patterns (expired, price reductions, DOM) | **Permitted** | This is a legitimate real estate business use |
| Storing MLS data in a local database for analysis | **Check your MLS** | Some MLSs restrict local storage; use API access where possible to avoid storing data |
| Using MLS data to contact expired listing sellers | **Check your MLS** | Some MLSs restrict solicitation of expired listings |
| Combining MLS data with public records data | **Permitted with caution** | The resulting combined dataset must still be used only for licensed real estate purposes and must not be shared |
| Displaying MLS data on a dashboard | **Check your MLS** | If the dashboard is only accessed by the licensed agent, this is generally permitted; if others access it, IDX/VOW rules may apply |
| Feeding MLS data into an AI/ML model | **Gray area** | No MLS has explicitly addressed this; consult your MLS and broker. At minimum, do not output or share raw MLS data from the model |

---

## 6. Data Privacy

### 6.1 CCPA / CPRA (California)

The California Consumer Privacy Act (CCPA), as amended by the California Privacy Rights Act (CPRA), applies to businesses that meet certain thresholds and collect personal information of California residents.

#### Applicability Thresholds (Must Meet One)

| Threshold | Detail |
|---|---|
| **Revenue** | Annual gross revenue exceeds $25 million |
| **Data volume** | Buys, sells, or shares personal information of 100,000+ California residents, households, or devices per year |
| **Revenue from data** | 50%+ of annual revenue from selling or sharing personal information |

**For most individual real estate agents**: You likely do not meet these thresholds. However, your brokerage might. And even if CCPA does not technically apply, following its principles is best practice and protects against future regulation.

#### Key Requirements (If Applicable)

| Requirement | Detail |
|---|---|
| **Notice at collection** | Must inform consumers at or before the point of collection about what personal information you collect and why |
| **Right to know** | Consumers can request disclosure of what personal information you have collected about them |
| **Right to delete** | Consumers can request deletion of their personal information (with exceptions) |
| **Right to opt out of sale/sharing** | Consumers can opt out of the sale or sharing of their personal information |
| **Right to correct** | Consumers can request correction of inaccurate personal information |
| **Non-discrimination** | Cannot discriminate against consumers who exercise their CCPA rights |
| **Data minimization** | Should only collect personal information reasonably necessary for the disclosed purpose |
| **Retention limits** | Should not retain personal information longer than necessary for the disclosed purpose |

### 6.2 Other State Privacy Laws

Several other states have enacted comprehensive privacy laws that may affect real estate lead generation:

| State | Law | Effective Date | Key Difference from CCPA |
|---|---|---|---|
| **Virginia** | Consumer Data Protection Act (VCDPA) | Jan 2023 | No private right of action; opt-in required for sensitive data |
| **Colorado** | Colorado Privacy Act (CPA) | Jul 2023 | Universal opt-out mechanism required; data protection assessments |
| **Connecticut** | CT Data Privacy Act (CTDPA) | Jul 2023 | Similar to Virginia; includes provisions for profiling |
| **Utah** | Consumer Privacy Act (UCPA) | Dec 2023 | Narrower scope; higher revenue threshold |
| **Iowa** | Consumer Data Protection Act | Jan 2025 | Limited consumer rights compared to CCPA |
| **Indiana** | Consumer Data Protection Act | Jan 2026 | Closely mirrors Virginia model |
| **Tennessee** | Information Protection Act (TIPA) | Jul 2025 | Includes an affirmative defense for following a privacy program |
| **Montana** | Consumer Data Privacy Act | Oct 2024 | Lower population threshold |
| **Oregon** | Consumer Privacy Act | Jul 2024 | Includes non-profit organizations |
| **Texas** | Data Privacy and Security Act (TDPSA) | Jul 2024 | Broad applicability; no revenue threshold |
| **Delaware** | Personal Data Privacy Act | Jan 2025 | Broad definition of personal data |
| **New Jersey** | Data Privacy Act | Jan 2025 | Broad consent requirements |
| **New Hampshire** | Privacy Act | Jan 2025 | Follows Connecticut model |
| **Nebraska** | Data Privacy Act | Jan 2025 | Applies to all businesses regardless of size |
| **Minnesota** | Consumer Data Privacy Act | Jul 2025 | Includes data broker registration requirements |
| **Maryland** | Online Data Privacy Act | Oct 2025 | One of the most restrictive; limits data use to what is strictly necessary |

### 6.3 Data Retention Best Practices

Regardless of whether you are legally required to comply with these laws, follow these best practices:

| Practice | Detail |
|---|---|
| **Define retention periods** | Set clear retention periods for different data types (lead data: 2 years inactive; client data: 7 years post-transaction for tax/legal purposes; marketing lists: review and purge annually) |
| **Document your policy** | Have a written data retention policy, even if simple |
| **Secure storage** | Use encrypted storage for personal information; use strong passwords and 2FA on all accounts |
| **Access controls** | Limit access to personal data to those who need it |
| **Deletion process** | Have a process for deleting data when retention periods expire or when a consumer requests deletion |
| **Vendor management** | Ensure your data vendors (CRM, email marketing, skip tracing services) also comply with applicable privacy laws |

### 6.4 Consent Management

| Type | When Required | How to Document |
|---|---|---|
| **Email marketing consent** | Not required under CAN-SPAM (opt-out model), but required for best practice and under some state laws | Web form submission, signup confirmation email |
| **Text/SMS consent** | Always required (TCPA) | Written/electronic signature with specific consent language; store timestamp, IP address (if online), and the exact consent language presented |
| **Phone consent** | Required only for autodialed/prerecorded calls (TCPA); DNC scrubbing required for all cold calls | DNC scrub records; consent forms for autodialed calls |
| **Data processing consent** | Required under CCPA/CPRA if selling or sharing personal information | Privacy notice acknowledgment; opt-out records |
| **Cookie consent** | Required under some state laws and for California residents | Cookie banner; preference center |

### 6.5 Handling Opt-Outs and Suppression Lists

| Requirement | Detail |
|---|---|
| **Universal suppression list** | Maintain a single, centralized suppression list across all channels (mail, phone, email, text) |
| **Cross-channel honoring** | If someone opts out via one channel, consider whether to suppress across all channels (legally required in some cases; always best practice) |
| **Permanence** | Opt-out requests should be honored permanently unless the consumer re-engages and explicitly opts back in |
| **Vendor sync** | Sync your suppression list with all vendors and systems that conduct outreach on your behalf |
| **Documentation** | Record the date, time, channel, and method of every opt-out request |
| **Never re-add** | Never re-add an opted-out person to your marketing lists, even if you encounter their information again through a different data source |

---

## 7. Record-Keeping Requirements

Maintaining thorough records is essential for defending against complaints and demonstrating compliance.

### 7.1 What Records to Maintain

| Record Type | What to Keep | Retention Period |
|---|---|---|
| **DNC scrub records** | Date of scrub, area codes scrubbed, source of DNC data, confirmation of scrub completion | 5 years |
| **Call logs** | Date, time, number called, agent who called, outcome, call duration | 5 years |
| **Email campaign records** | Date sent, recipient list (or list criteria), email content, unsubscribe count | 5 years |
| **Mail campaign records** | Date mailed, recipient list (or list criteria), copy of mail piece, quantity | 5 years |
| **Consent records** | Date consent obtained, method (web form, signed document), exact consent language presented, phone number/email authorized | Permanent (or until 5 years after last contact) |
| **Opt-out records** | Date of opt-out request, channel, method, person who made the request | Permanent |
| **Internal DNC list** | Phone numbers of people who requested not to be called, with the date of the request | Permanent |
| **Suppression list** | Master list of all people who have opted out of any outreach channel | Permanent |
| **Lead source documentation** | For each lead record: the data source, date obtained, and basis for outreach | Duration of lead record + 3 years |
| **Marketing material copies** | Copies of all marketing materials (mail pieces, email templates, scripts, social media ads) with dates used | 5 years |
| **Complaint records** | Any complaints received, how they were handled, outcome | 5 years |
| **Fair Housing training** | Records of Fair Housing training completed by the agent | Duration of license |
| **Broker approvals** | Documentation of broker review and approval of marketing materials | 5 years |

### 7.2 DNC Scrub Documentation

Every time you scrub a call list against the DNC registry, document:

```
DNC Scrub Record
================
Date of Scrub: [YYYY-MM-DD]
Area Codes Scrubbed: [list]
Federal DNC Registry Version: [date of data file]
State DNC Registry Used: [state, date of data file]
Total Numbers Before Scrub: [count]
Numbers Removed (Federal DNC): [count]
Numbers Removed (State DNC): [count]
Numbers Removed (Internal DNC): [count]
Total Numbers After Scrub: [count]
Performed By: [name]
System Used: [system name/version]
```

### 7.3 Consent Record Template

For each instance of consent obtained:

```
Consent Record
==============
Consumer Name: [name]
Phone Number / Email: [contact info]
Date of Consent: [YYYY-MM-DD HH:MM:SS timezone]
Method of Consent: [web form / signed document / verbal / text reply]
Consent Language Presented: [exact text of the consent disclosure]
Scope of Consent: [marketing calls / marketing texts / email marketing]
Specific Business Authorized: [your business name]
IP Address (if online): [IP]
Web Form URL (if online): [URL]
Witness/Verification: [how consent was verified]
Consent Revocation Date: [if revoked]
Revocation Method: [how revoked]
```

### 7.4 Opt-Out Tracking Template

```
Opt-Out Record
==============
Consumer Name: [name]
Contact Info: [phone / email / address]
Date of Opt-Out Request: [YYYY-MM-DD]
Channel of Request: [phone call / email / text reply / mail / in-person]
Exact Request: [what the consumer said or wrote]
Channels Suppressed: [all / phone only / email only / mail only / text only]
Processed By: [name]
Date Processed: [YYYY-MM-DD]
Confirmed Suppressed In:
  - [ ] CRM
  - [ ] Email marketing platform
  - [ ] Call list
  - [ ] Text platform
  - [ ] Mail list
  - [ ] All vendor systems
```

---

## 8. Compliance Checklist

Use this checklist before launching any outreach campaign.

### Pre-Campaign Checklist

#### Legal Foundation
- [ ] Confirmed which federal regulations apply to this campaign (DNC, CAN-SPAM, TCPA, Fair Housing, FCRA)
- [ ] Researched state-specific regulations for each state targeted
- [ ] Checked local/municipal ordinances for outreach restrictions
- [ ] Reviewed MLS terms of service for data usage restrictions
- [ ] All lead data sourced from legitimate, documented sources

#### Targeting & Messaging
- [ ] Lead targeting criteria do not reference or proxy for any protected class (federal or state)
- [ ] Geographic targeting is based on legitimate market criteria, not demographic composition
- [ ] Marketing message reviewed for Fair Housing compliance (language, images)
- [ ] No misleading claims about services or results
- [ ] Agent identified as licensed real estate agent with brokerage name
- [ ] License number included where required by state
- [ ] No exterior envelope/postcard references to distressing situations (foreclosure, divorce, death, bankruptcy)

#### Channel-Specific Compliance

**If Direct Mail:**
- [ ] Return address included
- [ ] Agent and brokerage identified
- [ ] Opt-out mechanism included (phone number, email, or return form)
- [ ] State-required disclosures included (especially for pre-foreclosure)
- [ ] Not mailing to anyone on the suppression list

**If Phone Calls:**
- [ ] Phone list scrubbed against federal DNC registry (within last 31 days)
- [ ] Phone list scrubbed against applicable state DNC registries
- [ ] Phone list scrubbed against internal DNC list
- [ ] DNC scrub documented with date and record counts
- [ ] Calling only during permitted hours (8 AM -- 9 PM recipient's local time, or stricter if state requires)
- [ ] Call script prepared with required identification and disclosures
- [ ] Manual dialing only (unless prior express written consent documented for auto-dialing)
- [ ] Call recording disclosure prepared (if in two-party consent state)
- [ ] Agent trained on opt-out handling (add to internal DNC immediately upon request)

**If Email:**
- [ ] Physical address included in email
- [ ] Unsubscribe link included and functional
- [ ] "From" name and email accurate
- [ ] Subject line not deceptive
- [ ] Email identified as advertisement (if commercial)
- [ ] Not emailing anyone on the suppression list
- [ ] Email list has not been purchased from an unverified source

**If Text / SMS:**
- [ ] Prior express written consent documented for EVERY recipient
- [ ] Consent records include: date, exact language, phone number, consumer signature
- [ ] Consent is specific to your business (one-to-one, per FCC 2025 rule)
- [ ] STOP keyword opt-out supported and tested
- [ ] Business name included in every message
- [ ] Sending only during permitted hours
- [ ] Not texting anyone on the suppression list

**If Door Knocking:**
- [ ] Local solicitation ordinance researched
- [ ] Solicitor permit obtained (if required)
- [ ] Real estate license and business cards carried
- [ ] Plan to respect "No Solicitation" signs
- [ ] Knocking only during appropriate hours
- [ ] Leave-behind materials prepared (not for mailboxes)

**If Social Media:**
- [ ] Housing ads use "Special Ad Category" on Facebook/Meta
- [ ] No targeting by protected class characteristics
- [ ] Agent and brokerage identified in profile/post
- [ ] FTC disclosures included where applicable
- [ ] Platform terms of service reviewed and followed

#### Data & Record-Keeping
- [ ] Lead source documented for every record in the campaign
- [ ] Consent records stored securely with timestamps
- [ ] Suppression list up to date and synced across all systems
- [ ] Campaign records (content, recipient criteria, dates) ready to be archived
- [ ] DNC scrub documentation filed

#### Review & Approval
- [ ] Marketing materials reviewed by managing broker
- [ ] Campaign plan reviewed against this checklist
- [ ] Agent has completed current Fair Housing training
- [ ] State-specific compliance requirements verified

---

## 9. Risk Mitigation

### 9.1 Common Mistakes Agents Make

| Mistake | Risk | How to Avoid |
|---|---|---|
| **Cold texting leads** | TCPA class action; $500--$1,500 per text | Never cold text. Only text with documented prior express written consent |
| **Not scrubbing DNC before calls** | $51,744 per call (federal); additional state penalties | Integrate DNC scrubbing as a mandatory automated step. Never skip it |
| **Using MLS data for non-real-estate purposes** | MLS suspension/termination; fines | Keep MLS data strictly within real estate business use |
| **Targeting by neighborhood demographics** | Fair Housing violation; HUD complaint; license action | Target by property characteristics (price, type, condition), not demographics |
| **Mailing "foreclosure" on a postcard** | State law violations; ethics complaints; license discipline | Always use envelopes for sensitive topics; never reference distress on exterior |
| **Ignoring "No Solicitation" signs** | Local ordinance violations; negative community perception | Train yourself to respect all no-solicitation signs |
| **Failing to honor opt-outs** | CAN-SPAM penalties; TCPA liability; state consumer protection violations | Process opt-outs immediately and sync across all systems |
| **Re-adding opted-out contacts** | Willful violation; treble damages | Maintain a permanent suppression list; check before every campaign |
| **Buying leads from questionable sources** | TCPA liability (you are responsible even if the vendor obtained the consent); poor lead quality | Verify consent documentation from lead vendors; use only reputable sources |
| **Using AI-generated content without review** | Fair Housing violations; misleading claims; unintended discriminatory language | Always have a human review AI-generated marketing content |
| **Contacting homeowners in foreclosure too early** | State law violations; criminal penalties in some states | Research your state's waiting period; when in doubt, wait 30+ days |
| **Not identifying as a licensed agent** | State license law violation; consumer deception | Include your name, brokerage, and license number in all communications |
| **Sharing MLS data with unlicensed persons** | MLS suspension/termination | MLS data stays within the licensed agent's use |
| **Ignoring state-level DNC lists** | State penalties in addition to federal | Scrub against both federal AND state DNC lists |

### 9.2 Penalty Summary

| Regulation | Maximum Penalty Per Violation | Who Enforces | Class Action Risk |
|---|---|---|---|
| **TCPA** | $1,500 (willful) | FCC, private right of action | **Extremely High** |
| **DNC / TSR** | $51,744 | FTC, state AGs | Moderate |
| **CAN-SPAM** | $51,744 | FTC, state AGs, ISPs | Low |
| **Fair Housing Act** | $105,194+ / unlimited (court) | HUD, DOJ, private right of action | Moderate |
| **FCRA** | $1,000 statutory / actual damages | FTC, CFPB, private right of action | High |
| **State foreclosure statutes** | Varies; criminal penalties in some states | State AG, state regulators | Low |
| **MLS violations** | $500--$15,000+ / suspension / expulsion | MLS board | N/A |
| **State license violations** | Fine, suspension, revocation | State real estate commission | N/A |

### 9.3 How to Protect Yourself

#### Structural Protections

1. **Work under your brokerage's compliance umbrella**: Ensure your broker has reviewed and approved all marketing campaigns
2. **Errors & Omissions (E&O) insurance**: Verify your E&O policy covers marketing and solicitation claims. Some policies exclude TCPA claims --- check and get a rider if needed
3. **Separate business entity**: Consider operating through an LLC to limit personal liability (consult an attorney for your specific situation)
4. **Written policies**: Document your compliance procedures in writing, even if you are a solo agent

#### Operational Protections

1. **Automate compliance checks**: Build DNC scrubbing, suppression list checking, and consent verification into your workflows so compliance is not optional or easily skipped
2. **Regular training**: Complete Fair Housing and compliance training annually, even if your state does not require it
3. **Vendor due diligence**: If using lead vendors, CRM systems, or outreach platforms, verify their compliance practices. You are ultimately responsible for compliance, not your vendors
4. **Audit regularly**: Conduct a quarterly self-audit of your marketing practices against this checklist
5. **Respond to complaints promptly**: If you receive a complaint, take it seriously. Respond promptly, document everything, and consult legal counsel if the complaint could escalate

#### If You Receive a Complaint

1. **Stop the campaign immediately** if the complaint relates to an active campaign
2. **Document everything**: The complaint, your records of the contact, consent records (if any), DNC scrub records
3. **Consult your broker** immediately
4. **Consult a TCPA/telemarketing attorney** if the complaint involves phone calls or texts (these escalate to lawsuits quickly)
5. **Do not contact the complainant** to try to resolve it directly (this can be seen as retaliation or further harassment)
6. **Preserve all records** --- do not delete anything related to the campaign or the complainant
7. **Review and fix** the process that led to the complaint

### 9.4 Insurance Considerations

| Coverage Type | What It Covers | Notes |
|---|---|---|
| **E&O insurance** | Professional negligence, errors in real estate transactions | May or may not cover marketing/solicitation claims --- check your policy |
| **General liability** | Bodily injury, property damage (e.g., door-knocking incidents) | Typically included in business insurance |
| **TCPA coverage** | Defense and damages from TCPA claims | Often EXCLUDED from standard E&O --- you may need a separate rider or standalone TCPA policy |
| **Cyber liability** | Data breaches, unauthorized access to consumer data | Increasingly important as you store more personal data digitally |

---

## Appendix A: Quick Reference by Outreach Channel

| Channel | Key Regulations | Risk Level | Pre-Campaign Must-Do |
|---|---|---|---|
| **Direct Mail** | Fair Housing, State licensing rules, State foreclosure statutes | **Low** | Review materials for Fair Housing; include required disclosures; check suppression list |
| **Phone Calls** | DNC (federal + state), TCPA, Fair Housing, Call recording laws | **Moderate-High** | Scrub DNC lists; prepare script with ID; manual dial only; check recording consent state |
| **Email** | CAN-SPAM, State email laws, Fair Housing | **Moderate** | Include unsubscribe link, physical address, accurate headers; check suppression list |
| **Text / SMS** | TCPA (highest risk), Fair Housing | **Very High** | Document prior express written consent for EVERY recipient; support STOP keyword |
| **Door Knocking** | Local ordinances, Trespassing, Fair Housing | **Low** | Check local permit requirements; carry license; respect no-solicitation signs |
| **Social Media Ads** | Fair Housing, Platform ToS, FTC disclosures | **Moderate** | Use Special Ad Category; no protected-class targeting; identify as agent |

---

## Appendix B: Key Regulatory Resources

| Resource | URL | Purpose |
|---|---|---|
| **National DNC Registry (Telemarketer Access)** | telemarketing.donotcall.gov | Scrub phone lists against DNC |
| **FTC CAN-SPAM Guide** | ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business | Email compliance reference |
| **FCC TCPA Rules** | fcc.gov/general/telemarketing-and-robocalls | Autodialing and text rules |
| **HUD Fair Housing** | hud.gov/program_offices/fair_housing_equal_opp | Fair Housing guidance and filing |
| **NAR Legal Resources** | nar.realtor/legal | REALTOR-specific legal guidance |
| **State Real Estate Commissions** | arello.org (links to all state commissions) | State-specific licensing rules |
| **CFPB RESPA Guide** | consumerfinance.gov/policy-compliance/guidance/other/respa | RESPA compliance |

---

## Appendix C: Glossary

| Term | Definition |
|---|---|
| **ATDS** | Automatic Telephone Dialing System --- equipment that can store or produce numbers using a random or sequential number generator and dial those numbers |
| **CAN-SPAM** | Controlling the Assault of Non-Solicited Pornography and Marketing Act (2003) |
| **CCPA** | California Consumer Privacy Act (2018, effective 2020) |
| **CPRA** | California Privacy Rights Act (2020, effective 2023) --- amends and expands CCPA |
| **DNC** | Do Not Call (Registry) |
| **EBR** | Existing Business Relationship --- exemption from DNC rules based on a prior transaction or inquiry |
| **FCRA** | Fair Credit Reporting Act (1970) |
| **FOIA** | Freedom of Information Act --- applies to federal agencies; state equivalents exist |
| **FSBO** | For Sale By Owner |
| **IDX** | Internet Data Exchange --- system for displaying MLS listing data on agent websites |
| **MLS** | Multiple Listing Service |
| **NOD** | Notice of Default --- public filing initiating the foreclosure process |
| **RESPA** | Real Estate Settlement Procedures Act (1974) |
| **TCPA** | Telephone Consumer Protection Act (1991) |
| **TSR** | Telemarketing Sales Rule (FTC regulation implementing telemarketing restrictions) |
| **VOW** | Virtual Office Website --- system for displaying MLS data (including sold) to registered website users |

---

*This document is part of the TheLeadEdge research library. It is a reference document, not legal advice. All strategies must be verified with a licensed attorney and approved by your managing broker before implementation. Laws and regulations change frequently --- review this document at least annually and whenever entering a new market or launching a new outreach channel.*

*Cross-references: See [Public Records Strategies](public_records_strategies.md) Section 14 for lead-source-specific legal notes. See [Automation Integrations](automation_integrations.md) Section 9 for technical compliance implementation.*
