# AWS Workbench

## Personal AWS, Data & AI Engineering Toolkit

> A practical engineering workbench for reusable AWS tools, data engineering utilities, machine learning workflows, AI/GenAI automation, infrastructure templates, packaging, and developer tooling.

**Build once. Reuse everywhere. Improve continuously.**

## 1. Overview

**AWS Workbench** is a personal engineering repository for turning real-world engineering work into reusable tools, automation, templates, workflows, and patterns.

The purpose is simple:

> **When a familiar engineering task appears, check AWS Workbench before solving it from scratch.**

If a reusable solution already exists, use it.

If it does not exist, build the solution, make it reusable, and add it to the workbench.

The repository is intentionally designed to grow over time through actual engineering experience rather than through a predefined collection of artificial examples.

## 2. Core Philosophy

AWS Workbench follows a **real-work-first** development model.

```text
Real Project
     │
     ▼
New Engineering Task
     │
     ▼
Check AWS Workbench
     │
     ├───────────────┐
     │               │
    Found          Not Found
     │               │
     ▼               ▼
   Reuse          Build
     │               │
     │               ▼
     │          Test & Refine
     │               │
     │               ▼
     │          Generalize
     │               │
     └───────┬───────┘
             ▼
      Add to Workbench
             │
             ▼
       Reuse in Future
```

The repository should continuously convert engineering experience into reusable capability.

---

## 🌎 Long-Term Vision

> Turn real-world AWS, Data, ML, and AI engineering experience into reusable tools and patterns.

Over time, CloudForge should become a personal engineering reference and automation platform where common tasks can be solved quickly instead of being rebuilt from scratch.

For example:

```text
Need a Lambda Layer?
        ↓
CloudForge
        ↓
Run the layer utility
        ↓
Select packages / runtime / region / account
        ↓
Build & package
        ↓
Publish
```

The same philosophy can eventually apply to:

* AWS infrastructure
* Data pipelines
* Machine learning workflows
* AI/GenAI applications
* Deployment workflows
* Packaging
* Monitoring
* Security
* Developer automation

---

# 🧩 Scope

CloudForge is organized around several major engineering areas.

## ☁️ AWS Engineering

Reusable utilities and automation for AWS services.

Potential areas include:

* Amazon S3
* AWS Lambda
* Lambda Layers
* IAM
* Amazon ECR
* API Gateway
* CloudWatch
* DynamoDB
* Step Functions
* EventBridge
* VPC
* STS
* Other AWS services as required

**TODO**

* [ ] S3 utilities
* [ ] Lambda utilities
* [ ] Lambda Layer builder
* [ ] IAM utilities
* [ ] ECR utilities
* [ ] API Gateway utilities
* [ ] CloudWatch utilities
* [ ] Additional AWS service utilities as needed

---

## 📊 Data Engineering

Tools and reusable patterns for building and managing data engineering workflows.

Potential areas include:

* Amazon S3
* AWS Glue
* Amazon Athena
* Amazon EMR
* Amazon Redshift
* AWS Lake Formation
* Data pipelines
* Data processing
* Data validation
* Data movement and synchronization

**TODO**

* [ ] S3 data utilities
* [ ] Glue utilities
* [ ] Athena utilities
* [ ] Data pipeline templates
* [ ] Data validation utilities
* [ ] Data processing utilities
* [ ] Additional data engineering utilities as required

---

## 🤖 Machine Learning

Reusable utilities and templates for machine learning workflows.

Primary focus includes **Amazon SageMaker AI** and supporting ML infrastructure.

Potential areas include:

* SageMaker AI
* Data processing
* Training jobs
* Model management
* Model deployment
* Endpoints
* Batch inference
* Pipelines
* ML infrastructure

**TODO**

* [ ] SageMaker processing utilities
* [ ] Training job utilities
* [ ] Model utilities
* [ ] Endpoint utilities
* [ ] Batch inference utilities
* [ ] SageMaker Pipeline templates
* [ ] ML deployment utilities
* [ ] Additional ML utilities as required

---

## 🧠 AI & Generative AI

Reusable tools and patterns for AI and Generative AI engineering.

Potential areas include:

* Amazon Bedrock
* Bedrock Agents
* Bedrock Knowledge Bases
* AgentCore
* Foundation models
* Prompt management
* AI application deployment
* AI infrastructure
* AI evaluation and testing

**TODO**

* [ ] Bedrock utilities
* [ ] Bedrock Agent utilities
* [ ] Knowledge Base utilities
* [ ] AgentCore utilities
* [ ] AI deployment templates
* [ ] Prompt engineering utilities
* [ ] AI evaluation utilities
* [ ] Additional AI tooling as required

---

# 🏗️ Infrastructure & Developer Tooling

CloudForge is not limited to Boto3.

The right tool should be used for the job.

Depending on the task, CloudForge may use:

* Python
* Boto3
* AWS CLI
* AWS CDK
* AWS SAM
* CloudFormation
* Docker
* Shell scripts
* Service-specific CLI tools
* Other AWS-supported tooling

**TODO**

* [ ] CDK templates
* [ ] SAM templates
* [ ] CloudFormation templates
* [ ] Docker templates
* [ ] CLI automation
* [ ] Deployment helpers

---

# 📦 Packaging & Build Automation

Reusable utilities for packaging and preparing applications for deployment.

Potential areas include:

* Lambda Layers
* Python packages
* Lambda deployment packages
* Docker images
* Dependency management
* Build automation

**TODO**

* [ ] Lambda Layer builder
* [ ] Python packaging utilities
* [ ] Deployment package utilities
* [ ] Docker build utilities
* [ ] Dependency automation

---

# 🔐 AWS Account & Region Management

CloudForge is designed to work across multiple AWS accounts and regions.

A common foundation will provide reusable handling for:

* AWS profiles
* Account selection
* Region selection
* Boto3 sessions
* Credentials
* STS
* IAM roles
* Environment configuration

The goal is to avoid rewriting account and region handling inside every utility.

Example:

```text
Select AWS Account
        ↓
Select Region
        ↓
Create AWS Session
        ↓
Run CloudForge Utility
```

**TODO**

* [ ] Reusable Boto3 session factory
* [ ] AWS profile selection
* [ ] Account validation
* [ ] Region selection
* [ ] STS AssumeRole support
* [ ] Common AWS configuration
* [ ] Common logging and error handling

---

# 📁 Project Structure

The repository will evolve over time.

The structure is intentionally modular so new utilities can be added without changing the overall concept.

```text
cloudforge/
│
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── config/
│   └── accounts.example.yaml
│
├── core/
│   ├── aws_session.py
│   ├── account_manager.py
│   ├── region_manager.py
│   └── logger.py
│
├── aws/
│   ├── s3/
│   ├── lambda/
│   ├── api_gateway/
│   ├── iam/
│   ├── ecr/
│   └── cloudwatch/
│
├── data/
│   ├── glue/
│   ├── athena/
│   ├── emr/
│   ├── redshift/
│   ├── lakeformation/
│   └── pipelines/
│
├── ml/
│   └── sagemaker/
│       ├── training/
│       ├── processing/
│       ├── pipelines/
│       ├── models/
│       ├── endpoints/
│       └── deployment/
│
├── ai/
│   ├── bedrock/
│   │   ├── agents/
│   │   └── knowledge_bases/
│   │
│   └── agentcore/
│       ├── create/
│       ├── update/
│       ├── deploy/
│       └── templates/
│
├── infrastructure/
│   ├── cdk/
│   ├── sam/
│   └── cloudformation/
│
├── automation/
│   ├── boto3/
│   ├── aws_cli/
│   └── scripts/
│
├── packaging/
│   ├── lambda_layers/
│   ├── python/
│   └── docker/
│
├── templates/
│   ├── lambda/
│   ├── ai/
│   ├── agentcore/
│   └── cdk/
│
└── projects/
    ├── active/
    └── archive/
```


---

# 🛠️ Development Model

CloudForge follows a **real-work-first** development model.

A utility should generally be added when a real engineering task demonstrates that it could be useful again.

### Example

Suppose a project requires:

```text
Lambda Layer
    ↓
Python packages
    ↓
Specific runtime
    ↓
Build package
    ↓
Publish Layer
```

If this task is likely to happen again, the solution can become:

```text
CloudForge
└── packaging
    └── lambda_layers
        └── build_layer.py
```

The next time the same problem appears, the utility can be reused instead of rebuilt.

---

# 📂 Project-Specific Code

CloudForge should remain focused on **reusable engineering capabilities**.

Project-specific application code should not automatically become part of the toolkit.

Temporary project work can live under:

```text
projects/
├── active/
└── archive/
```

When a project contains something generally reusable:

```text
Project Code
     ↓
Identify reusable component
     ↓
Generalize
     ↓
Move into CloudForge
     ↓
Reuse in future projects
```

This keeps the repository useful without turning it into a collection of unrelated project code.

---

# 🔒 Security

CloudForge must never store credentials or secrets in the repository.

Do not commit:

* AWS access keys
* Secret keys
* Session tokens
* API keys
* Passwords
* Private credentials
* Production secrets
* Customer-specific sensitive configuration

Preferred authentication mechanisms include:

* AWS CLI profiles
* IAM roles
* STS AssumeRole
* IAM Identity Center
* Environment-based credentials
* Other AWS-supported authentication mechanisms

Sensitive configuration files should be excluded through `.gitignore`.

Example:

```text
config/
├── accounts.example.yaml
└── accounts.yaml        # local only
```

---

# 🧱 Design Principles

CloudForge follows several principles.

### 1. Reusability

Build utilities so they can be reused across projects.

### 2. Practicality

Prioritize tools that solve real engineering problems.

### 3. Modularity

Keep utilities independent and composable where possible.

### 4. Multi-Account & Multi-Region

AWS utilities should not assume a single account or region.

### 5. Tool Agnostic

Use Boto3, AWS CLI, CDK, SAM, CloudFormation, Docker, or other appropriate tooling depending on the problem.

### 6. Progressive Growth

Do not build unnecessary infrastructure before it is needed.

### 7. Continuous Improvement

Existing utilities should be improved when real usage reveals better approaches.

### 8. Production Mindset

Even personal utilities should favor:

* Clear errors
* Logging
* Validation
* Safe defaults
* Reproducibility
* Maintainability

---

# 🗺️ Roadmap

CloudForge does not have a fixed feature-complete roadmap.

It will evolve based on real engineering needs.

## Phase 1 — Foundation

**TODO**

* [ ] Repository foundation
* [ ] Common configuration
* [ ] AWS session management
* [ ] Account management
* [ ] Region management
* [ ] Logging
* [ ] Error handling
* [ ] Basic CLI conventions

## Phase 2 — AWS Utilities

**TODO**

* [ ] S3
* [ ] Lambda
* [ ] Lambda Layers
* [ ] IAM
* [ ] ECR
* [ ] API Gateway
* [ ] CloudWatch

## Phase 3 — Data Engineering

**TODO**

* [ ] Glue
* [ ] Athena
* [ ] EMR
* [ ] Redshift
* [ ] Lake Formation
* [ ] Data pipelines

## Phase 4 — Machine Learning

**TODO**

* [ ] SageMaker processing
* [ ] Training
* [ ] Models
* [ ] Endpoints
* [ ] Batch inference
* [ ] Pipelines
* [ ] Deployment

## Phase 5 — AI & Generative AI

**TODO**

* [ ] Bedrock
* [ ] Agents
* [ ] Knowledge Bases
* [ ] AgentCore
* [ ] AI deployment
* [ ] AI evaluation
* [ ] Prompt tooling

## Phase 6 — Developer Automation

**TODO**

* [ ] CDK utilities
* [ ] SAM utilities
* [ ] CloudFormation templates
* [ ] Docker automation
* [ ] CLI automation
* [ ] Reusable project templates

---

# 🔄 Continuous Evolution

CloudForge is intended to be a long-term repository.

Its contents will change as new engineering challenges appear.

```text
New Problem
     ↓
Solve It
     ↓
Use It
     ↓
Identify Reusable Parts
     ↓
Generalize
     ↓
Add to CloudForge
     ↓
Improve Through Real Usage
     ↓
Reuse
```

Over time, the repository should become increasingly valuable because it represents **actual engineering experience converted into reusable assets**.

---

# 📌 Current Status

CloudForge is in its initial development stage.

The repository will start small and expand incrementally.

**Current priority:**

**TODO**

* [ ] Initialize repository
* [ ] Add project configuration
* [ ] Build AWS session/account/region foundation
* [ ] Add first reusable AWS utility
* [ ] Establish CLI conventions
* [ ] Establish utility documentation conventions

---

# 🎯 Long-Term Goal

The ultimate goal of CloudForge is simple:

> **When I encounter a familiar AWS, Data, ML, or AI engineering task, I should first check CloudForge before building it again from scratch.**

If the required utility exists:

```text
Find → Configure → Run → Reuse
```

If it does not exist:

```text
Build → Generalize → Add → Reuse
```

CloudForge should continuously turn experience into reusable engineering capability.

---

## ⭐ Philosophy

> **Build once. Reuse everywhere. Improve continuously.**

---

## 📄 License

**TODO**

Choose an appropriate open-source or personal-use license before publishing the repository publicly.

This version keeps the **identity and theme stable**, while the actual AWS/Data/ML/AI utilities are deliberately left as TODOs. That means six months from now, you can keep adding real tools without needing to redesign the README's core concept.


---




# 3. Long-Term Vision

AWS Workbench is intended to become a long-term personal engineering platform.

Over time it should contain reusable solutions across:

* AWS infrastructure
* Cloud automation
* Data engineering
* Machine learning
* Generative AI
* AI agents
* Deployment
* Packaging
* Monitoring
* Security
* Infrastructure as Code
* Developer productivity

The goal is not to predict every future requirement.

The goal is to **capture useful solutions as they appear in real work**.

---

# 4. What Belongs in AWS Workbench?

A component generally belongs in the workbench when it has one or more of the following characteristics:

* It solves a recurring engineering problem.
* It is useful across multiple projects.
* It can be generalized without customer-specific logic.
* It reduces repetitive manual work.
* It provides a reusable deployment or development pattern.
* It automates a common AWS operation.
* It provides a useful template or starting point.
* It represents a proven engineering pattern.
* It improves developer productivity.

### Example

A project requires a Lambda Layer containing several Python packages.

The first implementation may be project-specific.

If the task is likely to happen again, extract the reusable part:

```text
Project
   │
   ▼
Build Lambda Layer
   │
   ▼
Identify reusable logic
   │
   ▼
Generalize configuration
   │
   ▼
AWS Workbench
   │
   └── packaging/
       └── lambda_layers/
           └── build_layer.py
```

Future projects can then reuse the utility.

---

# 5. What Does NOT Belong?

AWS Workbench should not become a dumping ground for unrelated project code.

Avoid adding:

* Customer-specific business logic
* Hardcoded production configuration
* Temporary debugging scripts
* One-off experiments with no reusable value
* Secrets or credentials
* Customer data
* Large application implementations that are not reusable
* Duplicate versions of the same utility

Project-specific code should remain under:

```text
projects/
├── active/
└── archive/
```

If a reusable component is discovered inside a project, extract and generalize it before adding it to the appropriate workbench area.

---

# 6. Engineering Domains

AWS Workbench covers four primary engineering domains plus supporting infrastructure and automation.

---

## 6.1 AWS Engineering

Reusable utilities for AWS services and cloud operations.

Potential services include:

* Amazon S3
* AWS Lambda
* Lambda Layers
* IAM
* AWS STS
* Amazon ECR
* API Gateway
* CloudWatch
* DynamoDB
* Step Functions
* EventBridge
* VPC
* Secrets Manager
* Systems Manager
* Other AWS services as required

Examples of possible utilities:

```text
aws/
├── s3/
├── lambda/
├── iam/
├── ecr/
├── api_gateway/
├── cloudwatch/
└── ...
```

### Example use cases

* Inspect an S3 bucket.
* Count objects.
* Find large files.
* Synchronize files.
* Create or update Lambda functions.
* Copy Lambda functions between accounts.
* Build and publish Lambda Layers.
* Inspect IAM policies.
* Create ECR repositories.
* Query CloudWatch logs.

---

# 6.2 Data Engineering

Reusable utilities and patterns for AWS-based data engineering.

Potential technologies include:

* Amazon S3
* AWS Glue
* Amazon Athena
* Amazon EMR
* Amazon Redshift
* AWS Lake Formation
* Data Catalog
* Data pipelines
* ETL/ELT
* Data validation
* Data movement
* Data transformation

Possible structure:

```text
data/
├── glue/
├── athena/
├── emr/
├── redshift/
├── lakeformation/
└── pipelines/
```

### Example use cases

* Create or inspect Glue resources.
* Execute Athena queries.
* Inspect data lake structures.
* Validate datasets.
* Create reusable ETL templates.
* Automate data movement.
* Build reusable pipeline components.

---

# 6.3 Machine Learning

Reusable utilities for machine learning engineering and MLOps.

Primary AWS focus:

**Amazon SageMaker AI**

Potential areas include:

* Processing jobs
* Training jobs
* Models
* Endpoints
* Batch transform / inference
* Model deployment
* Pipelines
* Model monitoring
* ML infrastructure
* Experiment workflows

Possible structure:

```text
ml/
└── sagemaker/
    ├── processing/
    ├── training/
    ├── models/
    ├── endpoints/
    ├── pipelines/
    └── deployment/
```

The ML area should focus on reusable engineering patterns rather than storing individual model projects.

---

# 6.4 AI & Generative AI

Reusable utilities and patterns for modern AI engineering.

Potential technologies include:

* Amazon Bedrock
* Bedrock Agents
* Bedrock Knowledge Bases
* Foundation models
* AgentCore
* AI agents
* Prompt engineering
* RAG
* Evaluation
* AI application deployment
* AI infrastructure

Possible structure:

```text
ai/
├── bedrock/
│   ├── agents/
│   └── knowledge_bases/
│
├── agentcore/
│   ├── create/
│   ├── update/
│   ├── deploy/
│   └── templates/
│
├── prompts/
└── evaluation/
```

Examples:

* Create/update Bedrock resources.
* Inspect Knowledge Bases.
* Automate Bedrock Agent operations.
* Create AgentCore project structures.
* Maintain reusable AI deployment templates.
* Automate repetitive GenAI infrastructure tasks.
* Store reusable AI engineering patterns.

---

# 6.5 Infrastructure as Code

AWS Workbench should support multiple infrastructure approaches.

The repository is **not limited to Boto3**.

The appropriate tool should be selected for the problem.

Potential technologies:

* AWS CDK
* AWS SAM
* CloudFormation
* AWS CLI
* Boto3
* Docker
* Service-specific tooling

Possible structure:

```text
infrastructure/
├── cdk/
├── sam/
└── cloudformation/
```

### Guideline

Use:

```text
Boto3
```

when programmatic AWS API interaction is appropriate.

Use:

```text
AWS CLI
```

for straightforward command-line automation.

Use:

```text
CDK / SAM / CloudFormation
```

when infrastructure should be defined and deployed declaratively.

Use:

```text
Docker
```

when containerization or reproducible build environments are required.

The workbench should use the **right tool for the job**.

---

# 6.6 Packaging & Build Automation

Reusable packaging and build utilities.

Potential areas:

* Lambda Layers
* Lambda deployment packages
* Python packages
* Docker images
* Dependency packaging
* Build environments
* Deployment artifacts

Possible structure:

```text
packaging/
├── lambda_layers/
├── python/
└── docker/
```

Example:

```text
Build Lambda Layer
       │
       ├── Runtime
       ├── Python version
       ├── Dependencies
       ├── Architecture
       └── Output location
             │
             ▼
        Build package
             │
             ▼
       Publish Layer
```

---

# 6.7 Automation

General developer and cloud automation that does not belong to a specific AWS service.

Possible structure:

```text
automation/
├── boto3/
├── aws_cli/
└── scripts/
```

Examples:

* Environment setup
* Repetitive CLI workflows
* Multi-account operations
* File processing
* Deployment helpers
* Repository automation
* Developer productivity scripts

---

# 7. AWS Account & Region Management

Multi-account and multi-region support is a foundational requirement.

Utilities should avoid assuming that there is only one AWS account or one region.

The common AWS foundation should provide reusable mechanisms for:

* AWS profiles
* Account selection
* Region selection
* Boto3 sessions
* Credential resolution
* STS AssumeRole
* IAM Identity Center
* Environment credentials
* Account validation

Conceptually:

```text
Select Profile / Account
          │
          ▼
     Validate Account
          │
          ▼
     Select Region
          │
          ▼
    Create AWS Session
          │
          ▼
    Run Workbench Tool
```

All service-specific utilities should reuse this foundation instead of independently implementing account and region handling.

---

# 8. Configuration

Configuration should be separated from implementation.

Example:

```text
config/
└── accounts.example.yaml
```

Local configuration may contain information such as:

* AWS profile names
* Account aliases
* Default regions
* Environment names
* Non-secret preferences

Example:

```yaml
accounts:
  development:
    profile: my-dev-profile
    region: us-east-1

  staging:
    profile: my-staging-profile
    region: us-east-1

  production:
    profile: my-production-profile
    region: us-east-1
```

Actual local configuration should not be committed if it contains private information.

---

# 9. Security Rules

Security is a core repository requirement.

### Never commit:

* AWS access keys
* AWS secret keys
* Session tokens
* API keys
* Passwords
* Private credentials
* Production secrets
* Customer credentials
* Customer data
* Sensitive environment files

Preferred authentication mechanisms:

* AWS CLI profiles
* IAM roles
* STS AssumeRole
* IAM Identity Center
* Environment-based credentials
* AWS-supported credential providers

AWS Workbench utilities should rely on the standard AWS credential chain whenever practical.

---

# 10. Repository Structure

The repository is intentionally modular.

```text
aws-workbench/
│
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .editorconfig
│
├── config/
│   └── accounts.example.yaml
│
├── core/
│   ├── __init__.py
│   ├── aws_session.py
│   ├── account_manager.py
│   ├── region_manager.py
│   ├── config.py
│   └── logger.py
│
├── aws/
│   └── README.md
│
├── data/
│   └── README.md
│
├── ml/
│   └── README.md
│
├── ai/
│   └── README.md
│
├── infrastructure/
│   └── README.md
│
├── packaging/
│   └── README.md
│
├── automation/
│   └── README.md
│
├── templates/
│   └── README.md
│
└── projects/
    ├── active/
    └── archive/
```

### Important

Do not create every possible subdirectory immediately.

Directories should generally be introduced when the first real utility for that area is created.

For example:

```text
aws/
└── lambda/
```

should be created when Lambda tooling is actually added.

This prevents a repository full of empty directories.

---

# 11. Core Layer

The `core/` package provides functionality shared by multiple utilities.

Potential responsibilities:

```text
core/
├── aws_session.py
├── account_manager.py
├── region_manager.py
├── config.py
└── logger.py
```

### `aws_session.py`

Responsible for creating reusable Boto3 sessions and clients/resources.

### `account_manager.py`

Responsible for account/profile selection and account validation.

### `region_manager.py`

Responsible for region selection and validation.

### `config.py`

Responsible for loading and validating configuration.

### `logger.py`

Provides consistent logging behavior across utilities.

---

# 12. Utility Design Principles

Every reusable utility should aim to be:

### Reusable

Avoid project-specific assumptions.

### Configurable

Do not hardcode values that users should be able to change.

### Safe

Validate inputs before performing destructive operations.

### Observable

Provide useful logging and meaningful errors.

### Composable

Reuse common functionality from `core/`.

### Testable

Separate AWS interaction, configuration, and business logic where practical.

### Documented

A future user should understand:

* What the utility does.
* Why it exists.
* Required inputs.
* Required permissions.
* How to run it.
* What it produces.
* Any limitations.

---

# 13. Naming Conventions

Use clear, descriptive names.

Prefer:

```text
build_layer.py
copy_function.py
create_repository.py
inspect_bucket.py
deploy_agent.py
run_query.py
```

Avoid:

```text
test.py
final.py
new.py
script2.py
temp.py
helper.py
```

Directories should generally represent the AWS service, engineering domain, or capability.

---

# 14. CLI Design

Where practical, reusable utilities should expose a consistent command-line interface.

Example:

```bash
python -m aws.lambda.layers.build_layer
```

or:

```bash
python -m aws.lambda.layers.build_layer \
    --runtime python3.12 \
    --region us-east-1 \
    --packages boto3 requests
```

The exact CLI convention may evolve as the project grows.

The important principle is consistency.

---

# 15. Documentation Requirements

Reusable utilities should contain enough documentation to be independently usable.

At minimum, document:

```text
Purpose
Inputs
Outputs
Prerequisites
AWS permissions
Usage
Examples
Known limitations
```

For complex utilities, also document:

```text
Architecture
Workflow
Failure scenarios
Security considerations
```

---

# 16. Testing

Utilities that interact with AWS should be designed so that logic can be tested without unnecessarily calling real AWS resources.

Potential testing layers:

```text
Unit Tests
    ↓
Mock AWS Calls
    ↓
Integration Tests
    ↓
Optional Real AWS Environment
```

**TODO**

* [ ] Establish pytest configuration
* [ ] Add common test utilities
* [ ] Add Boto3 mocking strategy
* [ ] Define integration-test conventions
* [ ] Define test naming conventions

---

# 17. Project Isolation

Customer or project-specific implementations should remain separate from reusable utilities.

```text
projects/
├── active/
│   ├── project-a/
│   └── project-b/
│
└── archive/
    └── completed-project/
```

A project may initially contain experimental code.

Once reusable functionality is identified:

```text
Project-specific implementation
             │
             ▼
       Identify pattern
             │
             ▼
         Generalize
             │
             ▼
      Move to Workbench
```

This keeps AWS Workbench focused on reusable engineering assets.

---

# 18. Templates

Templates are reusable starting points rather than executable utilities.

Potential areas:

```text
templates/
├── lambda/
├── ai/
├── agentcore/
├── cdk/
├── sam/
└── ...
```

Examples:

* Lambda project template
* Bedrock Agent template
* AgentCore application template
* CDK stack template
* SAM application template
* Data pipeline template
* SageMaker project template

Templates should remain generic enough to be reused.

---

# 19. Kiro Usage

AWS Workbench is designed to work well with **Kiro** as an engineering assistant.

The README should be treated as the primary high-level repository reference.

When working inside this repository, Kiro should understand that:

1. This is a reusable personal engineering toolkit.
2. New functionality should be evaluated for reusability.
3. Project-specific business logic should not automatically be added to the workbench.
4. Existing utilities should be searched before creating new ones.
5. Common functionality should be reused rather than duplicated.
6. AWS account and region handling should use the shared `core/` layer.
7. Secrets and credentials must never be committed.
8. The appropriate AWS technology should be selected for each task.
9. Utilities should be documented and testable.
10. Repository structure should grow organically.

### Before creating a new utility

Kiro should conceptually follow:

```text
Understand Requirement
        ↓
Search Existing Workbench
        ↓
Can Existing Utility Be Reused?
        │
   ┌────┴────┐
   │         │
  Yes        No
   │         │
   ▼         ▼
Reuse    Design New Utility
             │
             ▼
       Identify Shared Logic
             │
             ▼
       Implement & Test
             │
             ▼
          Document
             │
             ▼
       Add to Workbench
```

---

# 20. Future Kiro Instructions

As the repository grows, Kiro-specific instructions may be added.

Potential future structure:

```text
.kiro/
├── steering/
├── specs/
└── hooks/
```

These files should contain detailed repository-specific development rules without making `README.md` unnecessarily implementation-heavy.

For example:

```text
.kiro/
└── steering/
    ├── architecture.md
    ├── coding-standards.md
    ├── aws-standards.md
    ├── security.md
    └── testing.md
```

The README remains the **high-level source of truth**, while Kiro steering files can contain detailed development instructions.

---

# 21. Development Workflow

The preferred workflow is:

```text
1. Identify repetitive task
        ↓
2. Search Workbench
        ↓
3. Reuse existing capability if possible
        ↓
4. If unavailable, design a reusable solution
        ↓
5. Implement
        ↓
6. Test
        ↓
7. Validate against real requirement
        ↓
8. Remove project-specific assumptions
        ↓
9. Document
        ↓
10. Add to Workbench
        ↓
11. Reuse in future projects
```

---

# 22. Example: Lambda Cross-Account Utility

A real-world requirement might be:

> Copy an existing Lambda function from one AWS account to another.

The initial solution may involve:

* Reading source Lambda configuration.
* Downloading the deployment package.
* Selecting destination account.
* Selecting destination region.
* Creating or updating the destination function.
* Recreating environment configuration where appropriate.
* Handling layers.
* Handling IAM roles.
* Validating the deployment.

Instead of leaving this as a one-off project script, the reusable solution could become:

```text
aws/
└── lambda/
    └── copy_function.py
```

Future improvements can then support:

```text
Single Function
       ↓
Multiple Functions
       ↓
Cross-Account
       ↓
Cross-Region
       ↓
Configuration Options
       ↓
Validation
```

The utility grows through real usage.

---

# 23. Example: Lambda Layer Builder

Another real-world requirement:

```text
Packages
   +
Python Runtime
   +
Architecture
   +
Build Environment
        ↓
Lambda Layer
```

The reusable utility could eventually provide:

```bash
aws-workbench lambda layer build
```

with configurable:

* Runtime
* Python version
* Architecture
* Packages
* Output directory
* AWS account
* AWS region
* Layer name
* Publishing behavior

This is an example of the type of repetitive engineering task AWS Workbench is intended to eliminate.

---

# 24. Roadmap

AWS Workbench intentionally does not have a fixed feature-complete roadmap.

The repository should grow according to actual engineering needs.

## Phase 1 — Foundation

**TODO**

* [ ] Repository initialization
* [ ] Python project configuration
* [ ] Shared AWS session management
* [ ] Account/profile management
* [ ] Region management
* [ ] Configuration management
* [ ] Logging
* [ ] Error handling
* [ ] CLI conventions
* [ ] Testing conventions

## Phase 2 — AWS Utilities

**TODO**

* [ ] S3 utilities
* [ ] Lambda utilities
* [ ] Lambda Layer builder
* [ ] IAM utilities
* [ ] ECR utilities
* [ ] API Gateway utilities
* [ ] CloudWatch utilities

## Phase 3 — Data Engineering

**TODO**

* [ ] Glue utilities
* [ ] Athena utilities
* [ ] EMR utilities
* [ ] Redshift utilities
* [ ] Lake Formation utilities
* [ ] Data pipeline utilities
* [ ] Data validation utilities

## Phase 4 — Machine Learning

**TODO**

* [ ] SageMaker processing utilities
* [ ] Training utilities
* [ ] Model utilities
* [ ] Endpoint utilities
* [ ] Batch inference utilities
* [ ] Pipeline utilities
* [ ] Deployment utilities

## Phase 5 — AI & GenAI

**TODO**

* [ ] Bedrock utilities
* [ ] Bedrock Agent utilities
* [ ] Knowledge Base utilities
* [ ] AgentCore utilities
* [ ] AI deployment templates
* [ ] Prompt utilities
* [ ] Evaluation utilities

## Phase 6 — Infrastructure & Automation

**TODO**

* [ ] CDK templates
* [ ] SAM templates
* [ ] CloudFormation templates
* [ ] Docker utilities
* [ ] AWS CLI automation
* [ ] Developer productivity utilities

---

# 25. Continuous Improvement

AWS Workbench is not expected to remain static.

A utility may start simple:

```text
Version 1
Simple reusable script
```

Then evolve:

```text
Version 2
Configuration
```

Then:

```text
Version 3
Multi-account / multi-region
```

Then:

```text
Version 4
Validation + logging + testing
```

Then:

```text
Version 5
CLI + documentation + automation
```

The goal is not to over-engineer version one.

The goal is to **improve useful tools through real usage**.

---

# 26. Quality Principles

Every addition should aim to satisfy the following:

### Correctness

The utility should perform the intended operation reliably.

### Safety

Destructive operations should require appropriate validation and safeguards.

### Reusability

Avoid hardcoded project-specific assumptions.

### Maintainability

Prefer clear code over clever code.

### Consistency

Follow established Workbench conventions.

### Observability

Errors should explain what went wrong and where possible how to fix it.

### Security

Never compromise credential or customer-data security for convenience.

### Documentation

Future reuse should be easier than rebuilding the solution.

---

# 27. Technology Direction

AWS Workbench may use any appropriate technology required by the engineering problem.

Primary technologies may include:

### Languages

* Python
* Bash / Shell
* Other languages when justified

### AWS

* Boto3
* AWS CLI
* AWS CDK
* AWS SAM
* CloudFormation
* Amazon SageMaker AI
* Amazon Bedrock
* AgentCore
* AWS Glue
* Amazon Athena
* Amazon S3
* AWS Lambda
* Amazon ECR
* CloudWatch
* IAM
* Other AWS services

### Development

* Git
* GitHub
* Docker
* pytest
* Kiro
* Other developer tooling as required

---

# 28. Repository Maturity

AWS Workbench should evolve through the following maturity model:

```text
Personal Script
      ↓
Reusable Script
      ↓
Reusable Utility
      ↓
Well-Tested Utility
      ↓
CLI Tool
      ↓
Reusable Engineering Component
```

Not every script needs to reach the final stage.

The level of engineering should be proportional to its usefulness and reuse potential.

---

# 29. Guiding Rule

When deciding whether something should be added, ask:

> **"Will I realistically benefit from having this available the next time I encounter a similar problem?"**

If yes:

**Generalize it and add it.**

If no:

**Keep it project-specific.**

---

# 30. Ultimate Goal

The ultimate purpose of AWS Workbench is to reduce repeated engineering effort.

Instead of:

```text
Problem
   ↓
Research
   ↓
Write script
   ↓
Debug
   ↓
Repeat months later
   ↓
Research again
   ↓
Rewrite script
```

the desired workflow is:

```text
Problem
   ↓
Search AWS Workbench
   ↓
Reuse
   ↓
Configure
   ↓
Run
   ↓
Improve if necessary
```

And when a capability does not exist:

```text
New Problem
   ↓
Build Solution
   ↓
Generalize
   ↓
Add to AWS Workbench
   ↓
Never solve the same problem from scratch again
```

---

# 31. Core Principle

> **AWS Workbench is not a collection of scripts.**
>
> **It is a continuously evolving engineering system built from real-world AWS, Data, ML, and AI experience.**

---

## Build once. Reuse everywhere. Improve continuously.

### One important recommendation

I would **not** create `.kiro/steering/` on day one unless you already have enough repository-specific rules to justify it. Start with the README as the architectural reference, then once you have several utilities, add:

```text
.kiro/
└── steering/
    ├── architecture.md
    ├── aws-standards.md
    ├── coding-standards.md
    ├── security.md
    └── testing.md
```
