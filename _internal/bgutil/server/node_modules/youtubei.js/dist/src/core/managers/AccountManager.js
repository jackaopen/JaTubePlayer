import AccountInfo from '../../parser/youtube/AccountInfo.js';
import Settings from '../../parser/youtube/Settings.js';
import NavigationEndpoint from '../../parser/classes/NavigationEndpoint.js';
import { InnertubeError } from '../../utils/Utils.js';
import { AccountItem } from '../../parser/nodes.js';
export default class AccountManager {
    #actions;
    constructor(actions) {
        this.#actions = actions;
    }
    async getInfo(all = false) {
        if (!this.#actions.session.logged_in)
            throw new InnertubeError('You must be signed in to perform this operation.');
        if (!all && !!this.#actions.session.context.user.onBehalfOfUser) {
            throw new InnertubeError('Boolean argument must be true when "on_behalf_of_user" is specified.');
        }
        if (all) {
            const get_accounts_list_endpoint = new NavigationEndpoint({ getAccountsListInnertubeEndpoint: {
                    requestType: 'ACCOUNTS_LIST_REQUEST_TYPE_CHANNEL_SWITCHER',
                    callCircumstance: 'SWITCHING_USERS_FULL'
                } });
            const response = await get_accounts_list_endpoint.call(this.#actions, { client: 'WEB', parse: true });
            return response.actions_memo?.getType(AccountItem) || [];
        }
        const get_accounts_list_endpoint = new NavigationEndpoint({ getAccountsListInnertubeEndpoint: {} });
        const response = await get_accounts_list_endpoint.call(this.#actions, { client: 'TV' });
        return new AccountInfo(response);
    }
    /**
     * Gets YouTube settings.
     */
    async getSettings() {
        const browse_endpoint = new NavigationEndpoint({ browseEndpoint: { browseId: 'SPaccount_overview' } });
        const response = await browse_endpoint.call(this.#actions);
        return new Settings(this.#actions, response);
    }
}
//# sourceMappingURL=AccountManager.js.map