import Menu from '../classes/menus/Menu.js';
import Button from '../classes/Button.js';
import MenuServiceItem from '../classes/menus/MenuServiceItem.js';
import { InnertubeError } from '../../utils/Utils.js';
export default class ItemMenu {
    #page;
    #actions;
    #items;
    constructor(data, actions) {
        this.#page = data;
        this.#actions = actions;
        const menu = data?.live_chat_item_context_menu_supported_renderers;
        if (!menu || !menu.is(Menu))
            throw new InnertubeError('Response did not have a "live_chat_item_context_menu_supported_renderers" property. The call may have failed.');
        this.#items = menu.as(Menu).items;
    }
    async selectItem(item) {
        let endpoint;
        if (item instanceof Button) {
            if (!item.endpoint)
                throw new InnertubeError('Item does not have an endpoint.');
            endpoint = item.endpoint;
        }
        else {
            const button = this.#items.find((button) => {
                if (!button.is(MenuServiceItem)) {
                    return false;
                }
                const menuServiceItem = button.as(MenuServiceItem);
                return menuServiceItem.icon_type === item;
            });
            if (!button || !button.is(MenuServiceItem))
                throw new InnertubeError(`Button "${item}" not found.`);
            endpoint = button.endpoint;
        }
        if (!endpoint)
            throw new InnertubeError('Target button does not have an endpoint.');
        return await endpoint.call(this.#actions, { parse: true });
    }
    items() {
        return this.#items;
    }
    page() {
        return this.#page;
    }
}
//# sourceMappingURL=ItemMenu.js.map