# CRAWLSPACE PROJECT

This is a project for a textbased crawlergame in cli

## Project Structure

No defined yet, ask where to put files before adding them

## Code Standards

- Use Python code with modern standards

## Commit standards

Types

    Changes relevant to the API or UI:
        feat Commits that add, adjust or remove a feature to/of/from the API or UI
        fix Commits that fix an API or UI bug of a preceded feat commit
    refactor Commits that rewrite or restructure code without altering API or UI behavior
        perf Commits are special type of refactor commits that specifically improve performance
    style Commits that address code style (e.g., white-space, formatting, missing semi-colons) and do not affect application behavior
    test Commits that add missing tests or correct existing ones
    docs Commits that exclusively affect documentation
    build Commits that affect build-related components such as build tools, dependencies, project version, ...
    ops Commits that affect operational aspects like infrastructure (IaC), deployment scripts, CI/CD pipelines, backups, monitoring, or recovery procedures, ...
    chore Commits that represent tasks like initial commit, modifying .gitignore, ...

    All your commits have to be added to branches starting with "oc" you are never allowed to commit into other branches by yourself

## Commit Attribution

    - You have in your environment a variable called GITHUB-TOKEN use it to push changes
    the author is always "oc-user" when ai commits something by adding the author flag to each commit. dont change repository user settings
    - you are not allowed to merge into main directly. create pull requests that a human has to approve
