<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

${ utils.bike(listing, hide_button=True) }

<meta http-equiv="refresh" content="5; url=${ redirect_to }">

<div class="interstitial focussed">
    <img src="/images/interstitial.png" alt="rdirecting">
    <div class="progress progress-striped
     active">
        <div class="bar"
             style="width: 10%;"></div>
    </div>
    <p>redirecting to our payments processor for further verification...</p>
</div>

<%def name="jsdefs()">
    ${ parent.jsdefs() }
<script type="text/javascript">
    var initProgress = 10;
    setInterval(function () {
        $('.interstitial.focussed .bar').css({width: initProgress += 3});
    }, 500);
</script>
</%def>
