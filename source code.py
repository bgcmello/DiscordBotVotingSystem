# pip install discord.py

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents,proxy="")


class PollView(discord.ui.View):

  def setup_poll(self, choices):
    self.votes, self.user_votes = {c: 0 for c in choices}, {}
    for i, c in enumerate(choices):
      b = discord.ui.Button(
          label=f"{c} (0)",
          style=discord.ButtonStyle.secondary,
          custom_id=f"p_{i}",
      )

      async def cb(i_act: discord.Interaction, ch=c, btn=b):
        uid = i_act.user.id
        cur = self.user_votes.get(uid)

        if cur == ch:
          self.user_votes.pop(uid)
          self.votes[ch] -= 1
          msg = f"❌ Removed vote for **{ch}**."
        elif cur:
          self.votes[cur] -= 1
          self.votes[ch] += 1
          self.user_votes[uid] = ch
          msg = f"✅ Switched vote to **{ch}**!"
        else:
          self.user_votes[uid] = ch
          self.votes[ch] += 1
          msg = f"✅ Voted for **{ch}**!"

        await i_act.response.send_message(msg, ephemeral=True)

        for child, (k, v) in zip(self.children, self.votes.items()):
          child.label = f"{k} ({v})"

        embed = i_act.message.embeds[0]
        embed.clear_fields()
        for k, v in self.votes.items():
          embed.add_field(name=k, value=f"{v} votes", inline=False)

        await i_act.message.edit(embed=embed, view=self)

      b.callback = cb
      self.add_item(b)


@bot.command()
@commands.has_permissions(administrator=True)
async def vote(ctx, *choices: str):
  if len(choices) < 2:
    return await ctx.send("Provide at least 2 choices.")
  view = PollView(timeout=None)
  view.setup_poll(choices)
  embed = discord.Embed(
      title="📊 Poll", description="Click a button to vote, switch, or remove."
  )
  for c in choices:
    embed.add_field(name=c, value="0 votes", inline=False)
  await ctx.send(embed=embed, view=view)

bot.run("")