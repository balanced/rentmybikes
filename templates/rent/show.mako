<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

${ utils.bike(listing) }

<div class="row">
    <div class="span7 box">
        <h1>Checkout</h1>
        <div class="span6 offset1">
            <form method="POST" id="purchase">
                ${ utils.csrf_token_input() | n }
                % if purchase_form or guest_purchase_form:
                    % if request.user.is_authenticated:
                    ${ form(purchase_form, False) }
                    % else:
                    <p>I already have an account.
                        <a href="${ url_for('login.index', redirect_uri=request.url) }">Sign me in</a>.</p>
                    ${ form(guest_purchase_form, True) }
                    % endif
                    <div class="actions">
                        <button class="btn btn-inverse">rent</button>
                    </div>
                % else:
                <p>We already have your payment details on file, click "rent" to rent<br>this bike.</p>
                <div class="actions">
                    <button class="btn btn-inverse">rent</button>
                </div>
                % endif
            </form>
        </div>
    </div>
</div>


<%def name="form(form, is_guest)">
    <%
        kwargs = {}
        if is_guest:
            kwargs['autofocus'] = 'autofocus'
    %>
    ${ utils.render_field(form.name, class_='span5', **kwargs) }
    ${ utils.render_field(form.email, class_='span5') }
    <%
        kwargs = {}
        if not is_guest:
            kwargs['autofocus'] = 'autofocus'
    %>
    ${ utils.render_field(form.card_number, class_='span5',
        autocomplete="off", **kwargs) }
    <div class="control-group">
        <label for="expiration_month">Expiration Date</label>
        ${ form.expiration_month(class_='span1') }
        ${ form.expiration_year(class_='span1') }
    </div>
</%def>
