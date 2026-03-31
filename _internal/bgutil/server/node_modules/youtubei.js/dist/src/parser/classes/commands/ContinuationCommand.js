import { YTNode } from '../../helpers.js';
export default class ContinuationCommand extends YTNode {
    static type = 'ContinuationCommand';
    #data;
    constructor(data) {
        super();
        this.#data = data;
    }
    getApiPath() {
        switch (this.#data.request) {
            case 'CONTINUATION_REQUEST_TYPE_WATCH_NEXT':
                return 'next';
            case 'CONTINUATION_REQUEST_TYPE_BROWSE':
                return 'browse';
            case 'CONTINUATION_REQUEST_TYPE_SEARCH':
                return 'search';
            case 'CONTINUATION_REQUEST_TYPE_ACCOUNTS_LIST':
                return 'account/accounts_list';
            case 'CONTINUATION_REQUEST_TYPE_COMMENTS_NOTIFICATION_MENU':
                return 'notification/get_notification_menu';
            case 'CONTINUATION_REQUEST_TYPE_COMMENT_REPLIES':
                return 'comment/get_comment_replies';
            case 'CONTINUATION_REQUEST_TYPE_REEL_WATCH_SEQUENCE':
                return 'reel/reel_watch_sequence';
            case 'CONTINUATION_REQUEST_TYPE_GET_PANEL':
                return 'get_panel';
            default:
                return '';
        }
    }
    buildRequest() {
        const request = {};
        if (this.#data.formData)
            request.formData = this.#data.formData;
        if (this.#data.token)
            request.continuation = this.#data.token;
        if (this.#data.request === 'CONTINUATION_REQUEST_TYPE_COMMENTS_NOTIFICATION_MENU') {
            request.notificationsMenuRequestType = 'NOTIFICATIONS_MENU_REQUEST_TYPE_COMMENTS';
            if (this.#data.token) {
                request.fetchCommentsParams = {
                    continuation: this.#data.token
                };
                delete request.continuation;
            }
        }
        return request;
    }
}
//# sourceMappingURL=ContinuationCommand.js.map