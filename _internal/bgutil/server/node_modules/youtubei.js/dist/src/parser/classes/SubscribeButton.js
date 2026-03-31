import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import SubscriptionNotificationToggleButton from './SubscriptionNotificationToggleButton.js';
import Text from './misc/Text.js';
export default class SubscribeButton extends YTNode {
    static type = 'SubscribeButton';
    button_text;
    subscribed;
    enabled;
    item_type;
    channel_id;
    show_preferences;
    subscribed_text;
    unsubscribed_text;
    unsubscribe_text;
    notification_preference_button;
    service_endpoints;
    on_subscribe_endpoints;
    on_unsubscribe_endpoints;
    subscribed_entity_key;
    target_id;
    subscribe_accessibility_label;
    unsubscribe_accessibility_label;
    constructor(data) {
        super();
        this.button_text = new Text(data.buttonText);
        this.subscribed = data.subscribed;
        this.enabled = data.enabled;
        this.item_type = data.type;
        this.channel_id = data.channelId;
        this.show_preferences = data.showPreferences;
        if (Reflect.has(data, 'subscribedButtonText'))
            this.subscribed_text = new Text(data.subscribedButtonText);
        if (Reflect.has(data, 'unsubscribedButtonText'))
            this.unsubscribed_text = new Text(data.unsubscribedButtonText);
        if (Reflect.has(data, 'unsubscribeButtonText'))
            this.unsubscribe_text = new Text(data.unsubscribeButtonText);
        this.notification_preference_button = Parser.parseItem(data.notificationPreferenceButton, SubscriptionNotificationToggleButton);
        if (Reflect.has(data, 'serviceEndpoints'))
            this.service_endpoints = data.serviceEndpoints.map((endpoint) => new NavigationEndpoint(endpoint));
        if (Reflect.has(data, 'onSubscribeEndpoints'))
            this.on_subscribe_endpoints = data.onSubscribeEndpoints.map((endpoint) => new NavigationEndpoint(endpoint));
        if (Reflect.has(data, 'onUnsubscribeEndpoints'))
            this.on_unsubscribe_endpoints = data.onUnsubscribeEndpoints.map((endpoint) => new NavigationEndpoint(endpoint));
        if (Reflect.has(data, 'subscribedEntityKey'))
            this.subscribed_entity_key = data.subscribedEntityKey;
        if (Reflect.has(data, 'targetId'))
            this.target_id = data.targetId;
        if (Reflect.has(data, 'subscribeAccessibility'))
            this.subscribe_accessibility_label = data.subscribeAccessibility.accessibilityData?.label;
        if (Reflect.has(data, 'unsubscribeAccessibility'))
            this.unsubscribe_accessibility_label = data.unsubscribeAccessibility.accessibilityData?.label;
    }
}
//# sourceMappingURL=SubscribeButton.js.map