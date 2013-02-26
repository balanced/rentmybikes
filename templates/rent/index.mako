<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

% for listing in listings:
${ utils.bike(listing) }
% endfor
