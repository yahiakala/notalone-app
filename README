# notalone

Follow the steps below to get started as a collaborator.

## Set up SSH on your machine

Setting up SSH is essential for secure communication. Below are the links to set up SSH for different operating systems.

- [Set up SSH on Windows](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
- [Set up SSH on Mac](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

## Set up a GitHub Account

If you do not have a GitHub account, create one by following the instructions on the [GitHub website](https://github.com/).

After creating your account, set up SSH with your GitHub account by following the instructions in this [GitHub guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).


## Fork this Repo

Click on the top right of this repo to fork it to your own account.

## Set up Amoni

Amoni is a tool that helps you manage your Anvil apps. To install and initialize Amoni, open your command line interface and run the following commands:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
ssh-add -l

amoni init myrepo
cd myrepo
amoni app add <github clone url> <name>
```

Replace <github clone url> with the clone URL of your forked GitHub repository and <name> with the name you want to give to your app.

## Set up Anvil Account

Create an account on the Anvil website if you do not have one already. It is recommended to set up a Personal Plan for more features and better support.

After creating your account, create a blank Anvil app. You will use this app to link your Amoni repository.

## Set up a Second Remote Repository

Set up a second remote repository with your blank Anvil app's SSH path. This will allow you to push and pull changes between your local machine and the Anvil app.

You are now ready to start developing your Anvil app. Happy coding!
