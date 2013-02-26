<%def name="render_field(field, **kwargs)">
% if field.type == 'HiddenField':
${ field }
% else:
<fieldset class="control-group ${ 'error' if field.errors else '' }">
% if kwargs.get('show_label', True):
${ field.label(class_="control-label") }
% endif
    <div class="controls">
        ${ field(**kwargs) }
        %if field.errors:
        %for error in field.errors:
        <div class="help-inline">${ error }</div>
        %endfor
        %endif
    </div>
</fieldset>
% endif
</%def>


<%def name="bike(listing, hide_button=False)">
<div class="box bike ${ listing.bike_type }">
    <div class="title">
        <h2>${ listing.title }</h2>
    </div>
    <div class="body">
        <div class="description">
            <p>${ listing.description }</p>
            <div class="price">
                <span>${ listing.price }</span>
                per day
            </div>
        </div>
        <div class="info">
            <div>
                <strong>Location</strong>
                <span>Palo Alto, CA</span>
            </div>
            <div>
                <strong>Type</strong>
                <span>${ listing.bike_type.title() }</span>
            </div>
            <div>
                % if not hide_button:
                <a href="${ url_for('rent.show', listing=listing.id) }" class="btn btn-inverse">Rent this bike</a>
                % endif
            </div>
        </div>
    </div>
</div>
</%def>

<%def name="csrf_token_input()">
<input type="hidden" name="_csrf_token" value="${session['_csrf_token']}">
</%def>
