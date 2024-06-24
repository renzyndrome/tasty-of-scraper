from InquirerPy.separator import Separator
from prompt_toolkit.shortcuts import prompt as prompt

import ofscraper.prompts.promptConvert as promptClasses
import ofscraper.utils.args.read as read_args
import ofscraper.utils.args.write as write_args
import ofscraper.utils.constants as constants
import ofscraper.api.statistics as stats
import ofscraper.utils.me as me_util
import logging
log = logging.getLogger("shared")

def action_prompt() -> int:
    action_prompt_choices = [*constants.getattr("actionPromptChoices")]
    action_prompt_choices.insert(3, Separator())
    action_prompt_choices.insert(6, Separator())
    action_prompt_choices.insert(9, Separator())
    answer = promptClasses.getChecklistSelection(
        message="Action Menu: What action(s) would you like to take?",
        choices=[*action_prompt_choices],
    )
    args = read_args.retriveArgs()
    action = constants.getattr("actionPromptChoices")[answer]
    if isinstance(action, str):
        return action
    if action == {'statistics'}:
        name, username = me_util.parse_user()
        me_util.print_user(name, username)
        log.info("Getting statistics")

        stats.get_earnings_all(username)
        stats.get_reach_guest(username)
        stats.get_reach_user(username)
        # stats.get_subs_fans_all(username)
        stats.get_subs_fans_earnings(username)
        stats.get_subs_fans_new(username)
        log.info("Finished downloading the statistics, please check the sheet")
        return True
    args.action = action
    write_args.setArgs(args)

    
