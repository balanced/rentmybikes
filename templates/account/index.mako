<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

<div class="row">
    <div class="span7 box">
        <h1>${ request.user.name }</h1>

        <div class="swell">
            <p>What would you like to do:</p>
            <a href="${ url_for('rent.index') }" class="btn btn-inverse">Rent a bike</a>
            <a href="${ url_for('list.index') }" class="btn btn-inverse">List a bike</a>
        </div>
    </div>
</div>
