# Syntrend CI Workflow

The overall branching convention uses Trunk-based development as this is releasing versioned products to external registries.

This requires that:

1. Each Feature and Bug being merged to `main` must by production ready.
2. Release Branches are created to...
  * allow cherry-picking of features/bugs to be included in a release.
  * isolate in-depth Release and UA Tests from an active `main` branch.

```mermaid
---
title: Branching Convention
config:
  gitGraph:
    showCommitLabel: false
---
gitGraph
    commit
    branch feat/new_feat
    commit
    checkout feat/new_feat
    commit
    commit
    checkout main
    commit
    branch bug/fix_issue
    checkout bug/fix_issue
    commit
    checkout feat/new_feat
    commit
    checkout main
    merge feat/new_feat
    checkout bug/fix_issue
    commit
    checkout main
    merge bug/fix_issue
    commit
    branch release/vX
    checkout release/vX
    commit tag:"vX"
    checkout main
    merge release/vX
```

```mermaid
---
title: Overall Workflow
---
flowchart
    classDef cond stroke-dasharray: 5 5
    
    trigger([Trigger])
    jbNewUnitTests[Identify and Run Work-specific Unit Tests]:::cond
    jbValVersion[ValidateVersion]:::cond
    jbUnitTests[Unit Tests]
    jbIntTests[Integration Tests]
    jbRepCov[Coverage Report]
    jbBuildWheel[Build Wheel]
    jbBuildContainer[Build Container]
    jbEndTests[End-to-End Tests]
    jbRegTests[Regression Tests]
    pause((pause))
    jbPublishTest[To Test Registries]:::cond
    jbRemOldBuilds[Remove Old Builds]:::cond
    jbPublishProd[To Public Registries]:::cond
    jbUAT[User Acceptance]
    jbTempBranch[Create Test Branch for Merge]:::cond
    jbMerge[Merge to Main]
    workflowEnd([End])
    
    trigger -.->|for Main| jbUnitTests
    trigger -.->|for PRs| jbNewUnitTests
    trigger -.->|for Release| jbValVersion
    jbNewUnitTests -.-> jbUnitTests
    jbValVersion -.-> jbUnitTests
    jbUnitTests --> jbIntTests
    jbIntTests --> jbRepCov
    jbRepCov --> jbBuildWheel
    jbBuildWheel --> jbBuildContainer --> jbEndTests --> jbRegTests -.->|for PRs and Main| jbPublishTest
    jbRegTests -.->|for Release| pause
    pause -.-> jbPublishProd
    pause -.-> jbUAT
    jbPublishProd --> jbMerge
    jbMerge --> workflowEnd
    jbPublishTest -.-> jbRemOldBuilds --> workflowEnd
    jbPublishTest -.-> jbUAT --> workflowEnd
    jbPublishTest -.->|for PRs| jbTempBranch --> workflowEnd
    
```

## Branch Rules and Workflows

### Pull Requests

Should include everything necessary for the changes are production ready and can be included in a release.

> [!NOTE]
> Objectives:
> 
> * includes unit/integration/end-to-end tests specific to the work being done
> * ensures no breaking changes to existing capabilities
> * ensures no breaking changes after a merge to main (through a temporary branch with both branches)
> * can build a package and pushed to the target registries (as test builds)
> * passes all tests (end-to-end tests all performed on both Wheel and Docker builds)

```mermaid
---
title: PR Workflow
---
flowchart
    trCommit([PR Trigger]) --> jbNewUnitTest[Identify and Run Work-specific Tests]
    jbNewUnitTest --> jbUnitTests[Unit Tests] & jbIntegrationTests[Integration Tests]
    jbUnitTests & jbIntegrationTests --> jbReportCov[Code Coverage Report]
    jbReportCov --> jbBuildWheel[Build Wheel] & jbBuildContainer[Build Container]
    jbBuildWheel & jbBuildDocker--> jbEndTests[End-to-End Tests]
    jbEndTests --> jbRegressionTests[Regression Tests]
    jbRegressionTests --> jbPublish[Publish Packages to Test Registries]
    jbPublish --> jbRemoveOldBuild[Remove old builds]
    jbPublish -.->|User Task| uat[User Acceptance]
    jbPublish -.->|Manual Trigger| jbTempBranch[Post-Merge Tests]
    jbTempBranch ~~~ n[Creates Temporary Branch\nwith main and the working branch\n\nRe-runs the PR Workflow\non the temporary branch]
    style n fill:#a82,color:#000
```

### Merge to Main

Repeats a lot of the some tests and functions done with PRs, but only focuses on production-readiness.

> [!NOTE]
> Objectives:
> 
> * includes unit/integration/end-to-end tests specific to the work being done
> * ensures no breaking changes to existing capabilities
> * can build a package and pushed to the target registries (as test builds)
> * passes all tests (end-to-end tests all performed on both Wheel and Docker builds)

```mermaid
---
title: Merge to Main
---
flowchart
    trCommit([Merge to Main]) --> jbUnitTests[Unit Tests] & jbIntegrationTests[Integration Tests]
    jbUnitTests & jbIntegrationTests --> jbReportCov[Code Coverage Report]
    jbReportCov --> jbBuildWheel[Build Wheel] & jbBuildContainer[Build Container]
    jbBuildWheel & jbBuildContainer--> jbEndTests[End-to-End Tests]
    jbEndTests --> jbRegressionTests[Regression Tests]
    jbRegressionTests --> jbPublish[Publish Packages to Test Registries]
    jbPublish --> jbRemoveOldBuild[Remove old builds]
    jbPublish -.->|User Task| uat[User Acceptance]
```

### Release Branch

Taking the work merged into `main`, the release branch will focus on combining the cherry-picked features from `main` and preparing any documentation and release notes.



Should include everything necessary for the changes are production ready and can be included in a release.

> [!NOTE]
> Objectives:
> 
> * includes unit/integration/end-to-end tests specific to the work being done
> * ensures no breaking changes to existing capabilities
> * ensures no breaking changes after a merge to main (through a temporary branch with both branches)
> * can build a package and pushed to the target registries (as test builds)
> * passes all tests (end-to-end tests all performed on both Wheel and Docker builds)
                                 
```mermaid
---
title: Release Workflow
---
flowchart
    trCommit([Release Commit]) --> jbVersion[Validates Version] 
    jbVersion --> jbUnitTests[Unit Tests] & jbIntegrationTests[Integration Tests]
    jbUnitTests & jbIntegrationTests --> jbReportCov[Code Coverage Report]
    jbReportCov --> jbBuildWheel[Build Wheel] & jbBuildContainer[Build Container]
    jbBuildWheel & jbBuildContainer--> jbEndTests[End-to-End Tests]
    jbEndTests --> jbRegressionTests[Regression Tests]
    jbRegressionTests --> taskIntervention([Workflow Pause])
    taskIntervention --> jbPublish[Publish Packages to Registries]
    jbPublish --> jbMergeMain[Merge to Main]
```

> [!NOTE]
> The last task (Merge to Main) is completed so 
> any bug fixes or corrections are made 
> available for all future releases.
