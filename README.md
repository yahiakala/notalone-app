# notalone

## Beginner - Develop in Anvil

First, create an Anvil account. You can run the app using the free plan, but I recommend the Hobby Plan which is approx 15 USD per month.

Complete this free course: https://training.talkpython.fm/courses/explore_anvil/anvil-web-apps-with-just-python

Fork this repository to your own GitHub user account. Click on the top right of this repo to fork it to your own account.

Follow this tutorial to clone the forked repository into your Anvil account: [https://anvil.works/docs/version-control-new-ide/git](https://anvil.works/docs/version-control-new-ide/git#cloning-a-github-repo-into-a-new-app)


## Advanced - Develop Locally
Follow the steps below to get started as a collaborator.

### Set up SSH on your machine

Setting up SSH is essential for secure communication. Below are the links to set up SSH for different operating systems.

- [Set up SSH on Windows](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
- [Set up SSH on Mac](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

### Set up a GitHub Account

After creating your GitHub account, set up SSH with your GitHub account by following the instructions in this [GitHub guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).


### Set up Amoni

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
