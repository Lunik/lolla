# Lolla

## Description

Lolla is a simple, easy to use, and lightweight Python binary for using Ollama's API. It is designed to be used in the terminal and can be used to make AI inference using Ollama's API.

## Installation

To install Lolla, simply run the following command:

```bash
pip install --user lolla
```

or with an isolated environment:

```bash
python -m venv ~/bin/lolla_venv
~/bin/lolla_venv/bin/pip install lolla

ln -s ~/bin/lolla_venv/bin/lolla ~/bin/lolla
```

## Usage

To use Lolla, simply run the following command :

```bash
lolla --help
```

## Contributing

To contribute to LaFlem, simply fork the repository and create a pull request. Please make sure to include a detailed description of your changes. Here are the things I will check during the review :

- Is CHANGELOG.md have been updated (**required**)
- Is the lint score did not decrease (**required**)
- Is the test coverage did not decrease (**required**)
- Is the documentation have been updated (**if required**)
- If tests have been added (**optional**)

### Development

This repository uses [Taskfile](https://taskfile.dev) to manage the development tasks. To see the available tasks, run the following command:

```bash
task --list
```