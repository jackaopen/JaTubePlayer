import Text from '../misc/Text.js';
import NavigationEndpoint from '../NavigationEndpoint.js';
import { YTNode } from '../../helpers.js';
export default class KidsCategoryTab extends YTNode {
    static type = 'KidsCategoryTab';
    title;
    category_assets;
    category_type;
    endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.category_assets = {
            asset_key: data.categoryAssets?.assetKey,
            background_color: data.categoryAssets?.backgroundColor
        };
        this.category_type = data.categoryType;
        this.endpoint = new NavigationEndpoint(data.endpoint);
    }
}
//# sourceMappingURL=KidsCategoryTab.js.map