import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import NavigationEndpoint from '../NavigationEndpoint.js';
import SectionList from '../SectionList.js';
export default class AnchoredSection extends YTNode {
    static type = 'AnchoredSection';
    title;
    content;
    endpoint;
    category_assets;
    category_type;
    constructor(data) {
        super();
        this.title = data.title;
        this.content = Parser.parseItem(data.content, SectionList);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.category_assets = {
            asset_key: data.categoryAssets?.assetKey,
            background_color: data.categoryAssets?.backgroundColor
        };
        this.category_type = data.categoryType;
    }
}
//# sourceMappingURL=AnchoredSection.js.map