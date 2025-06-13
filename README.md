## Target 🚀:
To resolve AWS SSO login using sso-session and to build or update the profile blocks in the local AWS configuration file accordingly. Based on this setup, you can then use other AWS profile switcher tools to switch roles more easily and make your life simpler.

## How to use
- Install kolja cli
    ```sh
    git clone https://github.com/koljahuang/kolja_aws.git
    cd project/root/dir
    poetry install
    ```
-  Nested Commands
    ```sh
    ~ kolja aws --help
    Usage: kolja aws [OPTIONS] COMMAND [ARGS]...

    Development commands.

    Options:
    --help  Show this message and exit.

    Commands:
    get
    login
    profiles
    set
    ```
- First, `kolja aws set` would guide you to set your sso session sections `[sso-session xxx]` in your local `~/.aws/config` file.

- Second, `kolja profiles` would help to create/update your profiles sections in your local `~/.aws/config` file, e.g.
    ```
    [profile 7777777777]
    sso_session = xxx
    sso_account_id = 7777777777
    sso_role_name = admin
    region = cn-north-1
    output = text
    ```

- Third, Choose to install your favorite `AWS profile switcher` and Feel free to switch accounts. Let's use [Granted](https://granted.dev/) as a demo 
    ```sh
    ~ assume -c
    ? Please select the profile you would like to assume:  [Use arrows to move, type to filter]

    > adminnx                        
    admin                          
    prod             
    ```