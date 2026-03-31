import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import Menu from './menus/Menu.js';
import MetadataBadge from './MetadataBadge.js';
import VideoViewCount from './VideoViewCount.js';
export default class VideoPrimaryInfo extends YTNode {
    static type = 'VideoPrimaryInfo';
    title;
    super_title_link;
    station_name;
    view_count;
    badges;
    published;
    relative_date;
    menu;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        if ('superTitleLink' in data)
            this.super_title_link = new Text(data.superTitleLink);
        if ('stationName' in data)
            this.station_name = new Text(data.stationName);
        this.view_count = Parser.parseItem(data.viewCount, VideoViewCount);
        this.badges = Parser.parseArray(data.badges, MetadataBadge);
        this.published = new Text(data.dateText);
        this.relative_date = new Text(data.relativeDateText);
        this.menu = Parser.parseItem(data.videoActions, Menu);
    }
}
//# sourceMappingURL=VideoPrimaryInfo.js.map