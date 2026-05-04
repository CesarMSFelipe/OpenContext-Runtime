# Technology Profiles

OpenContext Core is technology-agnostic. Profiles add stack-specific detection,
context-provider hints, workflow suggestions, and validation command suggestions
without changing core security defaults.

Profiles are optional. A project can match multiple profiles, such as
`node`, `react`, `docker`, and `github_actions`.

## First-Party Profiles

The first-party registry currently includes more than 230 profile detectors.

Generic and strategic profiles:

- `generic`
- `drupal`
- `symfony`
- `laravel`
- `node`
- `react`
- `next`
- `python`
- `django`
- `fastapi`
- `java_spring`
- `dotnet`
- `go`
- `rust`
- `rails`
- `wordpress`
- `terraform`
- `data_ml`

Frontend and JavaScript ecosystem:

- `javascript`
- `typescript`
- `deno`
- `bun`
- `vite`
- `webpack`
- `rollup`
- `parcel`
- `storybook`
- `jest`
- `vitest`
- `cypress`
- `playwright`
- `vue`
- `nuxt`
- `angular`
- `svelte`
- `sveltekit`
- `astro`
- `remix`
- `solid`
- `ember`
- `electron`
- `tauri`
- `react_native`
- `expo`
- `ionic`
- `capacitor`
- `qwik`
- `redwood`
- `blitz`
- `meteor`
- `gatsby`

Mobile:

- `flutter`
- `dart`
- `android`
- `ios`
- `swift`
- `kotlin`
- `kotlin_multiplatform`

Node backends:

- `express`
- `nestjs`
- `koa`
- `hapi`
- `adonis`

PHP, CMS, and commerce:

- `php`
- `composer`
- `cakephp`
- `codeigniter`
- `yii`
- `magento`
- `shopware`
- `prestashop`
- `shopify`
- `strapi`
- `directus`
- `payload_cms`
- `keystone`
- `sanity`
- `typo3`
- `joomla`
- `ghost`

Python and data engineering:

- `flask`
- `celery`
- `conda`
- `pipenv`
- `tox`
- `nox`
- `hatch`
- `uv`
- `scrapy`
- `airflow`
- `jupyter`
- `dbt`
- `spark`
- `dagster`
- `prefect`
- `great_expectations`
- `dvc`
- `mlflow`
- `ray`
- `kedro`
- `bentoml`
- `feast`

JVM and .NET:

- `maven`
- `gradle`
- `quarkus`
- `micronaut`
- `jakarta_ee`
- `scala`
- `aspnet`
- `blazor`
- `unity`

Native, functional, and systems languages:

- `cpp`
- `c`
- `cmake`
- `make`
- `bazel`
- `pants`
- `elixir`
- `phoenix`
- `erlang`
- `clojure`
- `haskell`
- `ocaml`
- `fsharp`
- `ruby`
- `r`
- `julia`
- `matlab`
- `lua`

DevOps, CI, and infrastructure:

- `docker`
- `kubernetes`
- `helm`
- `ansible`
- `pulumi`
- `cloudformation`
- `serverless`
- `aws_sam`
- `github_actions`
- `gitlab_ci`
- `azure_devops`
- `nix`
- `packer`
- `nomad`
- `aws_cdk`
- `cdk8s`
- `cdktf`
- `terragrunt`
- `opentofu`
- `bicep`
- `crossplane`
- `argocd`
- `fluxcd`
- `tekton`
- `jenkins`
- `circleci`
- `buildkite`
- `drone_ci`
- `woodpecker_ci`
- `dependabot`
- `renovate`
- `pre_commit`
- `semgrep`
- `trivy`
- `checkov`
- `snyk`
- `opa`

Observability and analytics platforms:

- `prometheus`
- `grafana`
- `opentelemetry`
- `elasticsearch`
- `opensearch`
- `kafka`
- `flink`
- `beam`
- `trino`
- `snowflake`
- `bigquery`
- `redshift`

Database, platforms, monorepos, and static sites:

- `prisma`
- `supabase`
- `hasura`
- `sql`
- `nx`
- `turborepo`
- `pnpm_workspace`
- `poetry`
- `hugo`
- `jekyll`
- `eleventy`
- `salesforce`
- `openapi`
- `graphql`
- `apollo`
- `grpc`
- `protobuf`
- `alembic`
- `flyway`
- `liquibase`

Games, blockchain, embedded, and agentic app stacks:

- `godot`
- `unreal`
- `bevy`
- `solidity`
- `hardhat`
- `foundry`
- `truffle`
- `anchor`
- `move`
- `cosmos_sdk`
- `substrate`
- `arduino`
- `platformio`
- `zephyr`
- `langchain`
- `llamaindex`
- `haystack`
- `semantic_kernel`
- `crewai`
- `autogen`

## Safety Rule

Suggested validation commands remain suggestions. They are not executed unless
the runtime action policy allows or approval-gates them.
