# Collaborative Slack Adventure game

Basically this runs Colossal Cave (from the bsdgames package) but connects its input and output to a Slack channel.

To run:

- Get yourself a Slack API token (I'm a bit confused about the various ways to do this, but one way is at https://api.slack.com/custom-integrations/legacy-tokens)
- Find out the channel ID of the channel you want to run this in. You can find channel IDs using the API tester at https://api.slack.com/methods/channels.list/test
- Ensure the user who owns the token is in the channel, so it will receive messages from the channel
- `CHANNEL_ID=... SLACK_TOKEN=... docker-compose up`
