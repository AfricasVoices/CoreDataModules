from core_data_modules.cleaners import Codes
from core_data_modules.cleaners.codes import SomaliaCodes


class DemographicPatterns(object):
    only_yes_no = r"^\W*(asc|ok)?\W*(ka+l?\W*ka+[kla]*|kalak|kalalak)?\W*ha+h?(ye)?\W*$|^\W*ha+h?(ye)?\W*(ka+l?\W*ka+[kla]*|ka(la)?ak)?\W*$|^\W*(ka+l?\W*ka+[kla]*|ka(la)?lak)?\W*hye\W*$|^\W*(ka+l?\W*ka+l|kalaka?|kalalak)?\W*ma*ya?\W*$"

    noise = r"^\W*(asc|ok)?\W*(ka+l?\W*ka+[kla]*|ka(la)?lak|kal)?\W*(asc|ok)?\W*$|^\W*330\W*$|^\W*mahad\ssanid\W*$|^\W*in\W*[cs]ha+\W*a?l+a*h?(alah)?\W*$|^\W*oke?y?\W*$|^\W*(ka+l?\W*ka+la?|kalaka?|kalalak)?\W*tir\W*tir\W*$|^\W*(hi|hello)\W*$|^\W*thanks\W*$|^\w\w?$|^fuck$|^\W*dal\W*dhis\W*$"

    genders = {
        Codes.MAN: r"\bm[ae]n|ra+[gqk]|wi+l|\bmal+e|\bmeal|\bbo[yi]|\bni+n|oday|rija+l|wa+laduq|a+be|\bna+n\b|\bni+n\b|raju+l|\br[ue]+g|\bwll\b|\bwil\b|brg\b\bmr\b|\bboy\b|(\b|\W)la+[bp][ao]?|kab|la+b|labo+d|\bla[xgpdma]\b|we+l|xasan|sadaam|a[xh]med|calisharif|lobo|laban|mujahid|labbaan|lb|\bl(\sa\s)*b\b|jab|\bm\b|abdi|axmed|cali|laba|\bla[ap]|\ble?b|lobo|\bleb|\bla[gmx]|ahaylab|l\sa\sb|lab[ao]|\b[jl]ab|lab+an+n|mujahid|\bmin|sadaam|\bwe+l|xasan|\blaf|\brag|rajul|wiil",
        Codes.WOMAN: r"wom[ae]n|d[aou]+m+[ua]r?|ga+ba*r|f[ae]mal+i*e*|femael|f[ea]m[ae]l[ie]|g[ai]rl|ho+yo|na+g|fahi+ma|famle|ga+ba+dh|ga[pbw]+a+r|ha+ba+r|hawe+n(ay)?|ho+yada\bna+k\b|femayl|caisha\bdum\b|\bdmr\b|hodan|dh*[aei]\s?[dt]+h*[ei][gkq]a*|ladig|dh[aei]g*d*[iu]+[dg]?|dheqdid|maamo|dhidd*ga*|dheed[di]i[gd]|dhe[s.]d*ig|dhig|lidig|d[bh][\si]dig|dakar|nimco|nadik|shadiig|marwo|gbr|giwar|fartun|inan|islan|dh!d!|\bf\b|barwaaqo|ladh?[ei]g|bhadig|cheddig|db[ai]dig|deeqo|d[gh]\sdi?g|dgadig|dh!d!|dh[ae]?\Wd+ig|dh[ae]+b?d+[aei]*g|dhagdd|dhalmabarad|dhaxig|\bdhed|dhe+[djs]+[io]?[dg]|dhid*g|fheddiga|fimel|\bgbr|ghdadig|giwar|iadig|\blan|marwo|\bnag|shadiig|dh[aei]?h?dig|dgedigd|dumar|digili|dnadig|gabadha|ledig|phadig|dhad[ij]g"
    }

    yes_no = {
        Codes.YES: r"\b\W*haa+h*\W*\b|\b\W*ye+s\W*\b|\b\W*haayes\W*\b|\b\W*xa+\W*\b",
        Codes.NO: r"\b\W*ma?ya\W*\b|\b\W*no\W*\b|\b\W*mayano\W*\b|\b\W*may[eo]*\W*\b|\b\W*m[ea]*y[ao]\W*\b|\bma\W*ya+g?\b|mayakalkal"
    }

    urban_rural = {
        Codes.URBAN: r"m[as]+[qkg]a+l+[ao]+[ld]*a*|mglo|maga*lada|daynile|ma*ga+l[eo]?|m[ou][gq]a?dish[ou]|\bluuk|g[oa]r[ao]+w*e|qarawe|groe|burco|mudug|ma ?[gj]+a+l*o|mga+lo|yaqshi+d|cad*ale|bardhere|d[ae]yni*le|wadajir|[gk]a*lka?cyo|afgo*ye|daynile|ca*simada|harg[aei]+y?i?sr?a|m[as]+ga*l[eo]|city|capital|m[ou][gq]a?di?sh[aou]|[gk]a+l[gk]a?c?[iy]o|baidoa|kisi?ma+yo|jow?har|ha?rga?ys|bu+ca|baydhabo|baidoa|bay ?dha ?bo|beled ?weyn|b[ae]y\s?dha\s?b[ao]|afgoi|baardhe+re|b\Wdhe+re|baidoa|beydhuwa|baydhoba|baladweyne|b\Wd?\W?weyne|balad\s?we+yne|b\Wweyn|blwn|b[ae[l[ae]d\s?we+yne|bo+s+[ao]+s+o|bosso|o+sa+so|bu+ho+dle|bu+l+o\W*bur[dt]e|bu+rco|bu+hodle|cabudwa+q|ce+ga+g|ce+ri\W?ga+bo|\bcegbo|dhu\W?sa\smare+b|\beyl|ga+l*ka*c*yo|ka+lgac*yo|glkcy|galcad|gal[kc]aio|glkcyo*|ga[cl]kio|ga*lmu+du+g|ga+l[gka]cyo?|ga+l\s?kaciy?o|ka+lkacyo|ga+lkcayo|[ck]alkaca?yo|gur[ai]?ce+l|ha+ra?\s?g[ae]+[yi]+a?sa*|hage[iy]sa|\bhar\b|harga+i?[sy]+(a|eis|pa)?|harge+r?[iy]+si?a|har+gesi?a?|hargi+[ey]?sa|hargsa|hargyisa*|harkeysa|hasgeis|\bhay\sb\b|hayaey|hragayas|\bhrg\b|hrgaysa|hrgsa|hrgwysa|hrgys|hrysa|harge+a+|hargies|j[ao]+w*har*|kisi?m+ayo|ko+d\sbu+r|la+sqo+ray|lafo+le|\bluuq|m[ou][gkq]a*d[yi]sh*x*[uo]|town|balcad|bu\Wa+le|jama+me|megalo|b\Wdhera|balacad|bardhere|b[ae]ydhabo|bo?saso|ca+simad|celasha|mhaybe|shibis|dharkenley|gaga+lo|guri?ce+l|hiliwa|m[aw]ga+\s?lo|mega+l|muqdish[io]|salax\slafte+da|town|ca+simad|\b[jl]u+k|bosa+so|ka+ra+n|ko+dbu+r|afgo+ye|axmed\W*dhagax|b\W*w[ae]yn|ba+r\W*dhe+r|baidoa|balcad|bana+dir|bardhe+r|b[ae]ydhabo|bo+sa+s[ao]|bula burte|burtinle|c\W*wa+q|ca+s[iu]mad|cadada|caynabo|ce+lasha|ce+ri?ga+bo|celafwen|dagmada\W*warta|dayni+ne|dharkey?nl[ae]y|dhu\W*samare+b|gabilye|gacan\W*libax|gal\*kacyo|garbahare+y|gargaysa|guri?\W*[cl]e+l|harg[ae]ysa|hargso|hodon|hol\W*wadag|hudur|ibra+hi[mn]\W*ko+dbu|jilib|jowhar|karn|khanddala|kisma+yo|libaax gar|\bluuq|m\W*agalo|m\W*glo|ma+glada\W*bosaso|\bmaalo|madalada|madino|\bmagaa|magaglo|magala|m[ao]gal[od]|magolo|magool madaxda|malagada|maxamed haybe|mo?ga?la?da|miyi|m[ou]qdisho|mugadishu|qandala|saakow|tieglow|tuulada|wadajir|wanla weyn|war dhigley|warta nabada|x\W*jajab|xafada ak toobar",
        Codes.RURAL: r"vil+ag[er]*|tu+[lt]+[0ou]|tu+lada|tu+l[anu]+|village|tu+rta|to+lu*|biln\sokatir|balcad|wardhi+g\s?le+|ba+diye|tu+led|xera+le|bo+sa+so|\beyl\b|ce+ri\W?ga+bo|rugey|burtile|hodan|guricel|tuvlo|guri?ce+l|hurwa+|barwa+qo|\bg[ae]do\b|lafo+le|badiyo|\btuio\b|mdije+x|dhanqare|wada ?[jri]+|\bhu+sh\b|\bkaran\b|borama|b\W*weyn|26\W?ju+n|a\W+dhagaxa|alaybaday|axmed\sdh?agax|baadiye|bacaadley|badiyaha|badiy[eo]|balcad|balese|bandar\sbayla|barsane|b[ae]y\s?dha+\s?bo|bal?ca+d\sley|ba+d+iy(aha|e|o)|balese|bandar\Wbayla|barsane|barwa+qo|baladxa+wo|biln\sokatir|biya\skulule|bocame|bohol|borama|bulashiq|burtin?le|\bbu+ca|\bbu+la\sbacley|ce+l\sdhe+r|ce+l\sja+le|dacabu+dh|da+bley|dalsan|dhanqare|dhoboolo[bp]|dhu+do|do+lo|fa+rax\so+mar|g\W*de+ble|g\W+liba+x|gacam\sliba+x|garso+r|\bg[ae]do|grada+gwh|hila+c|hodan|hurwa+|hu+sh|jazi+ra+d|johara|karan|maxamu+d\s?haye?be|m\Whaye?be|naga+d|\boog\b|qansaxdhe+re|qoryale|qudbacdhe+r|rasi\scaser|rugey|she+kh\bnu+r|she+q\bmaxa+d|shibi+s|su+qa\sxolaha|t[uv]+l+[eou]|tu+lp|tuluo|wada\s?j[ri]+|wardhi+g\sl[ey]+|xagu+ga|xamar|xerale|marka cadey|\b[bdt]uul?[io]|hantiwadag|miga|xafta calnley|ba+deyeah|baadiye|badhan|baliaxmed|balidhig|\bbeer|beral[ae]y|bulagadu|bul+axa+r|bura+n|ca+dley|cada+y\W*yuru+ra|da+rsala+m|daynu+nay|dega+nka beraha iyo xoolodhaqato|dhahar|durqsi|duulo|gradag|guburah|gu+ra+y|halgan|hergura an ahay|kaaraan|laasgeel|laba xad\W*dhexdood\W*oobanaan|lafoole|mayo+nto|miig|\bmiyi|nasiye|qod qod|qool\W*bu+lale|re+r\W*[bgk]u+ra|re+r m[ai]yi|sabawana+g|san\W*yare|xa+r\W*xa+r|\bxiis|xola ley|xoolo dhaqato+y|rugey"
    }

    numbers = {
        10: r'ten|towon|teen|\btoba+n',
        14: r'tobaniyoafaar',
        15: r'fi[vf]teen|tuban\siyo\sshan',
        16: r'lex\siyo\stabanjir',
        17: r'sevente*n|toba*n\siyo\stodobo|totobiyotoban',
        18: r'sideed\siyo\stoban',
        19: r'saga+l\si\stowan',
        20: r'twenty|la[bw]a+\s*tan',
        22: r'laba+ta+n\siyo\s?labo',
        23: r'labatad\Wiyo\Wsatax\Wsano',
        25: r'la[bw]a+\s*ta+n\siyo\shan',
        30: r'thirty|sod[ao]*n\sjir|sodonjir|3o',
        31: r'3I',
        34: r'sodon\Wiyo\Wafar\Wsano',
        35: r'sodo*n\siyo\shan',
        40: r'fourty|afartan',
        45: r'afratan\siyo\sshan',
        50: r'fifty|5o',
        1: r'one|mid|\bhal\b',
        2: r'two|la+ba+',
        3: r'three|sa+d+[ae]x',
        4: r'four|[ac]far|afarsano',
        5: r'five|shan',
        6: r'six|lix',
        7: r'seven|todobo',
        8: r'eight|sided',
        9: r'nine|sa+ga+l',
        0.5: r'\bbar\b'
    }

    mogadishu_sub_districts = {
        SomaliaCodes.BOONDHEERE: r"bo+n?\W*dh*e+re|bo+ndhe",
        SomaliaCodes.CABDLCASIIS: r"ab*d*i\W*a[sz]i[sz]|cabd?[ui]*l*ca[sz]i+[sz]|cabdi\s?ca[sz]i+|c\W*ca[sz]i+[sz]|c\W*casiis|cabda\W*casis|c\W*sisia|cabdul\W*casis",
        SomaliaCodes.DAYNILE: r"d[ea]+[iy]\W*ni*[kl]+[ae]|de+ya*ni+n*le|d[ae]yli+ne|day[mn][ei]+[ly]|de+ynu+ney|de+ni+le|de+nli+re|de+y\W*ni+o?l|dayni+[ln]|da+nile|teynile|dayi+le|dayne+li|deyni+\W*le|d[iy]+ni+le|daynike|daynle|da+yne+la|dayanile",
        SomaliaCodes.DHARKENLEY: r"dh*arkenley|dharkaynlay|dhark[ea]+y*nynle+y*|dhark[ae]+ley|dhar\W*ke+nkey|dharkeynley|dharke+nle*y|dharki+nle+|dha+rk[ei]+n[kl]e*y|darke+n?le|dharkeyley|dharke*nly|dhar\W*kay?n?\W*l[ae]*y|dh[ae]r\W*k[ei]+y?n?\W*l[aey]+|dhar\W*k[ei]n?|dhar\W*ge+y?n\W*le+y|dhara?ke[ny]?ly|\bdhi+gle\b|dhkiley|dhar\W*kenl|dhrkenly|dhar\W*ki+le|dharkay\sley|dharky?n?l?[ae]y|dhake+n\W*le+y|dherkaynley|dhrk*n?le?y|dhrkynley|drkly|dh?irkenley|dhar\W*[gk][ae]*yn\W*l[ae]*y|darkenkay",
        SomaliaCodes.HELIWA: r"hur[ui]+wa+|huruwaay|hurwa+|huruwa+|huru*wa+y*|h[ei]li?wa|hali\W*wa|heli\W*wa|hil[ai]+wa|hiriwa|hilwaa|horiwa|\bhiwaa\b",
        SomaliaCodes.HODAN: r"\bho+\W*d+[oa]*n|hu?dan|ho+\W*d+an",
        SomaliaCodes.HAWL_WADAAG: r"hawle|\bwadag|ho+lwada+g|\bwada+g|holwa+g|h[oa]+w?lwada+g|howl*wada+g|[hm]olwa+da+g|hor?wadaa[gq]|how?l\W*wada+k|\bwaag|holwada|how?lwd?ag|howlwag|hantiwada+g|\bhawda\b|hodawadag",
        SomaliaCodes.KARAAN: r"\bka+r[ai]+n|\bka+\W*ra+n|\bka+rn|\bkm\b|kraan",
        SomaliaCodes.SHANGAANI: r"shanga+ni|shan\s*ga+ni",
        SomaliaCodes.SHIBIS: r"\bsh[ai]bis|degmadash[ai]bis",
        SomaliaCodes.WAABERI: r"wa+b[aei]r[iy]|w\W*beri|\bwbri|wa+\W*beri",
        SomaliaCodes.WADAJIR: r"wada+j[ei]+r|wa+da+.*ji+r|wa+j[ie]+r|m[ea]dina|[d.]*wadh*[a\s]*jir*|wjer|faarax\saxmed|\bwadi\s?jir|wa[st]ajir|\bwdjr|wdjir",
        SomaliaCodes.WARDHIIGLEEY: r"wardh[ei]+gl[ae]*y|warta\s*nabada|war\s*dh*i+g\s*le+y|awdinley|w\W*dhi+glay|war\W*dhi+glay|wdhigle",
        SomaliaCodes.XAMAR_JAABJAB: r"ja+[b]?jab|[hx]amr\W*jjb",
        SomaliaCodes.XAMAR_WEYNE: r"[xh]amar*\W*we[yi]n[e]|[hx]\W*we+y?ne|[hx]\W*we+ne|[hx]amrweyn",
        SomaliaCodes.YAAQSHID: r"ya+q*s*hi+[dt]|\bya+q.*si+d|ya+pshi+d|ya+[rqk]a*[sh]s*hi+[dtg]s*|ya+[qkg]sh*i*d|ya+qas*hi+|ya+qa*\W*sh[ei]+|[xy]a+(q|kh)\W*sh"
    }

    somalia_districts = {
        SomaliaCodes.ADAN_YABAAL: r"\ba+dan\b|yaba+l",
        SomaliaCodes.AFGOOYE: r"afa?\s?g[ou]+ye*|\bgo+ye*|afg[io]+|agoye*|afo+ye|afgonye|c[ae]+la*sha*|\bla+fo+le*|afgoa|afkoyo|afio|afoi|la*\sfo+l+e|cay?lasha\W*biyaha|raaxoole|tulada barire|tuulada ceel wareegow|[ao]+wdhe+gle|carbis|[ao]carbis|ce+la\W*biyaha|\bmu+ri|ticsi+le|warmaxan|warmo+ley|afjo+ye|cumarbe+re|jambalul|jasir|af+oye|af\W*go|\bafg\b|afgaaye|agoi",
        SomaliaCodes.AFMADOW: r"afmado+w|mado+w|jana+\s?cabdal+e|qooqaani|dh?o+b\W*l[ae]+y|\bxagar|afa?mdow|calmadaw",
        SomaliaCodes.BAARDHEERE: r"ba*rdh?era?|[bp]a+r?\W*dh\W*e*r|b\W*dhe+re|ba+r\W*dh[ae]*re|ba+r\W*dhe|b\W*dher[ae]|bar\s?de+ra|bar\W*a?dhe+r|brdhe+ra|ku+rma+n|bldhere|mardhaa|\bbaar\b|berdhere|b\W*dhero|bardeere|berdhere|b\W*dher|b\W*berde|b\W*dera|b\W*dhe+r[ao]|\bbaar\b|ba+ra?dh?e+r|bar+dh*e+re",
        SomaliaCodes.BADHAADHE: r"ba+dha+dh?e|badhedhe|badha+he",
        SomaliaCodes.BAIDOA: r"[bp]ai?dob?a|baidao|be*ydha+bo|b[ea]*y? ?dha?[bh][ao]|berda+le|baydh?[ao](wa)?|ba+diyo|ba?y\W*dh[ao]+\W*[bw][aoy]|horse+d|bydowa|madi+na|b[ae]y\W*dh[ao]wa|biadoa|daynuney|goof\sgadu+t|awdi+n?le|galool|d[ae]y\W*nu+n[ae]y|xarunta gobolka hialaan|day\W*nu+ney|bydoa|manas|baidio|g\W*dhe+r|shonqolow|batdhabo|beydabo|dega+nka\W*ha+bare|medi+na|bayadhaw|bayadhaw|badhoba|bey\W*dha\W*bo|beydhawo|bydhw",
        SomaliaCodes.BAKI: r"\bbaki+\b|baysa+re|sab[ao]*\W*wana+g|sbwnag|baarka",
        SomaliaCodes.BALCAD: r"\bbal+i*c*ad\b|ba[kl]+\W*ca|bal+\W?ad\b|ba(la)?ca[ds]|balcas|balcd|baran|blcad|baca+d|garasdel|masaga\Wwey|damaley|gumar|warshi+[qkh]|bo+da+le|gara?sbintow|\bbalcat\b|\bgalcad\b|\bblcd\b",
        SomaliaCodes.BANDARBAYLA: r"b[ea][iy]la(ha)?\b|\bb[ea]nder|baligubadle|bixin|kodmo|ba+r\W*xayle",
        SomaliaCodes.BARAAWE: r"ba+ra+w[ae]|bra+we|baraabe",
        SomaliaCodes.BELET_WEYNE: r"bele[td]\W*we[iy]ne|\bb\w*wa*ne|bld\swey|\bb\w*w[ae]*[yi]ne*|\bb\w*we+[yi]*n|b\W*w[ae]+[iyv]n|beletwein|be*\W*la*d\W*weyn|ba?\W*w[ae]+[iy]n|b[ae]?/Wweye?n|b[ae]le[dt]\s?w[ae]yne?|blwey?n|b\W+w[ae]+yn?e?|ba?la[dt]weyn|bele?d\s?we+y?n?|b\Wwein|balatwe+n|bald\swe+yne|balwene|bld\s?wy?ne|bledwien|b\Wwyne|\bb\Wen|fe+r\W?fe+r|b\/w|farliba+x|ge+dlabe+na|jawi+l|mata\W*[bw]a+n|kabxanle+y|ba+rey|beladwn|blwn|ce+l\W*cali|co+ma+d|de+fo+w|dhagaxyale|galajir|galxamur|to+rabo+ra|xaw[ao]\W*ta+ko|bula\W*xa+wo|\bblw|blwexn|dacarata|xafada\W*koshin|balada\W*w[ae]+n|balada\W*w[ae]y*a*n|bald\W*w[ae]ya*n|baled\W*wein|b\W*wen|b\W*d\W*wyne|b\W*ld\W*w[ae]yn|b\W*ny|badwe+ne|bala+d\W*we+i*n|baladw[ae]*yn|baladwdn|baladwiene|bala[dt]\W*wey\W*n|balay\W*bane|balda*\W*wey*n|baldweyane|baled\W*wen|baled\W*wyn|bed\W*weyn|be+d\W*weyn|bel\W*we+n|beladmen|belda\W*weyine|beled\W*weyn|bl\W*weyn|bLad\W*we+ne|bld\W*w[eiy]+n|bledweym",
        SomaliaCodes.BELET_XAAWO: r"beledhawo|bele[dt]\W*[hx]a+w[ao]|bula\W*[hx]a+w[aeo]|b\Wxawo|b[ae]le*dxa+wo|beyaxa+wo|beladxa+wo|baladxawo|balaxawa|b\W*xa+wo|bala+da*\W*xa+w[ao]|balat\W*xawo|balaxawe|be+dhawo|beldhawo|bld\W*xawo",
        SomaliaCodes.BERBERA: r"b[ae]+r*\W*b[ae]+ra?|berbea|bul+[au]xa+r|abda+l|la+s\Wbarwa+qo|xaga+l|la+sci+dle",
        SomaliaCodes.BORAMA: r"bo+ra+[hm][oae]|bo+came|qulu?je+d|boame|maga+lacad|quluje+d|\bboon|xari+rad|we+ra+r|booram|dunbuluq|she+d\W*d?he+r|bo+rma|boram|\bbscu\b|bssso",
        SomaliaCodes.BOSSASO: r"b[ao]+[zs]+[oa]+s[ao]|bsa+so+|bo[sz]+[ao][sz]?|po+sa+so|be+nde+r\s*ca+s+im*|xafada\sla+g|bo+sa+bo|booso|b[0o]+\W?sa+[0os]|bo+s+\s?so|bsso|ca\W*rmo|gal\W?gala|ufayn|\barmo\b|biyo\W*kulale|dagmaufe+n|uf[ae]yn|yalho|carma+n|kalbayr|la+sa\W*dawaco|busasu|crmo|\blaag|\bqaw\b|so+sa+so|xaafada raf iyo raaxo|bo+[br]a+so|tisjiic|basso|pasaso|boc?\W*sa+so|bo+sa|busa+s",
        SomaliaCodes.BUAALE: r"bu\W*a+le|bulay|\bgol\W*jano|bu+ly",
        SomaliaCodes.BULO_BURTO: r"burdhubo|bu+l[ao]+\s*b[au]r\W*?[dt][eo]|bu+la+\s*brif|b[ou]+l+[ao]+\W*b[ou]+r[dt][eo]|bu+lo\s*burti|ma[xn]asa*|buulo bareer|b\W*b[au]r[dt][eo]|bu?\W*bu[rt]e|bali\sbusle|buulo|bu+la?\W*b[ou]?r[dt][eo]|celka\W*caliW*cumar|bu+l+a+y|buul[ae]|halgan|dhagaxya+l|ma[hx]a+s|bu+l[ae]\W*b[ae]r?[dt][ae]|moqokori|pulaay|bula\W*bur?t[ai]|bu\W*bu+r?te|bulo\W*bure|bulo\W*berde|bulu\W*borte|bu+l+[au]\W*b[au]rd|bu+lubare",
        SomaliaCodes.BURCO: r"burac?o|bu+r?co|\bbur\Wo\b|\bburan|burr?\W*co|\bburo|\bbuurod|ga+sha+mo|warcibra+n|balhile|bali\W*dhi+g|birca|\bburu?c|xa+jiW*sa+lax|duruqsi|bali\W*ji+la+l|bali\W*khayr|bali\W*calanle|bali\W*abokor|\bbeer|bilidhi+g|bookh|b[ou]rca?[0io]|burcm|buruc|dabaqabad|dhoqosh[ae]y|burc\W*co|dandan|october|warcibra+n|xa+ji\W*sa+la|duru*[khq]+shi|gediha+n|harad+a|nasiye|riyo\W*xidho|shansha+n?c?a?de|warci[bm]ra+n|agto+bar|oktkobar|burxo|\bderi|durqis|du+rukhusi|duruqsi|ina\W*af\W*mado+be|wra+be+ye|bucr|bo+co|buaco",
        SomaliaCodes.BURTINLE: r"bur\W*t[ei]n?l+e|bu+r+\W*[dt]\W*i?n?\W*le|[bp]u+r+\W*ti+n?l?e|bo+rtile|caga+ran|xasbahale|brtnle|buratil|burtle|cagaran|xas\W*bahale|bur\W*din\Wle",
        SomaliaCodes.BUUHOODLE: r"b[ou]+a?\W*ho+da?le|balihadhac|ce+ga+g|q[ou]r[iu]lu[dg]|buhdle|bu+ho+d|buhu+d?le|bu+dle|\bcayn\b|widh\W*widh|b[ou]+ho+dle|bohotle|bhdle|bu+ho+le|bu+hu+dla",
        SomaliaCodes.BUUR_HAKABA: r"bu+r\s?haka\W?[bw][ao]|\bha+ka+ba|xakaba|bu+r\s*haca+ba|bur\W*hakawo|bu+r\s?xaka\s?b|b\W*hakab[ao]|bu+hakabo|le+go|ba+riyo+w|ha+bare|buqW*aqable|bur+akabe",
        SomaliaCodes.CABUDWAAQ: r"c*a\W*[bpw]u+d?a?\W?wa+[pq]|c?a+[bt]u*dwa+k|\bca+bud|c\W*wa+q|c(\W*b)?\W*d\W*wa+q|c\W*budwa+g|ca+\W*bu+[dt]*\W*wa+q|abudqaw|c\W*(bud)?wa*q|ca?(ab)?u?[dt]u?\W*wa+q|xera+le|balanbale|abudwak|\bc/w|ca\W*[dw]+a+q|ca+\s*budwaq|cabud\swak|cawdaq|cudwaq|hera+le|huurshe|rera+le|sii\Wdhabal\Wyuu|\bc\Ww\Wq|\bc\W*w\b|balanbal|gcanlibax|bangele|ca\W*buduq|cawudq|cbdwq|\bcw[ad]*q|dhabad|xira+le|balanble|bohol|ca+wuda+q|ca?b[au]dwa+q|cadub\W*waq|cawudwaq|cbdw?q|kaxandha+le|mi+r\W*ji+c?l[ae]y|ooda+le|cbuwaq|abd[ou]dwa[gq]|c\W*bu*dwa*q|c\W*dwq|ca+bubud\W*wa+|ca+buwq|ca+buwq|ca+duwq|cabdu\W*wq|cab[io]d\W*wa+q|cabuwq|caduwq|cawbuda+q|clwa+q",
        SomaliaCodes.CADAADO: r"c*a+d+a+d[ao0]*|gur[ei]*\s*ce+l|gur[ia].*c*e+l|ca*d+ado|gurce+l|\bguri|kuricel|gali+n?\W*sor|gidhays|cdaado|geli+sor|bange+le|baxdox|bange+le|\bbaxdo|gurcaal|cada+dle|goracal|gura\W*ceyl|\bcad\b|cadaadmo|canado|curi\W*ce+l",
        SomaliaCodes.CADALE: r"\bc*a+da+d*le\b|calan\W*lay|cabaye|calalaale|calanley|cerdacle|co+danle|garas\W*dhe+ra|cadaalay|cadadal[ae]y|cadaley|cadalo+w|cadan",
        SomaliaCodes.CALUULA: r"alu+la|calu+l*a|qa+lu+l|cal+a+[uw]la|murcanyo|xaabo",
        SomaliaCodes.CAYNABO: r"c*a[iy]nab[oa]|sara+r|\boog\b|dhana+no|wadam[ao]go|ce+nabo|higlo|warida+d",
        SomaliaCodes.CEEL_AFWEYN: r"afwe+[iy]n|ce+l\W*af[iy][ae]+[iy]n|afwe+i?n|\bhulu+l|ce+l\W*afwf?[ae]*y?n?|garadag|xe+dho|calfwen|ci+l\W*afway|dhu+rcila+n|[dg]aradag|camuud|la+s\W*ci+dle",
        SomaliaCodes.CEEL_BARDE: r"ce+l\W*bar?d",
        SomaliaCodes.CEEL_BUUR: r"ce+l\W*bu+[hr]|el\s*bu+r|derri|gal\W*hare+ri|xayow|dhagax\W*ya+le|gubato|wabxo|celn\W*bur|ceylbur",
        SomaliaCodes.CEEL_DHEER: r"ce+l\W*dh*e+r|ce+ldahir|go+hwayne|c\W*dhe+r",
        SomaliaCodes.CEEL_WAAQ: r"el\s*wa+[qk]|ce+la*\W*[uw]a+[kqg]",
        SomaliaCodes.CEERIGAABO: r"c*e+rigai*[bv]o|ce+ri*\s?g|crgbo|celqalo+w|c\Wga+bo|ce(ri)?\W?ga+bo|xin?galo+l|awrbo+gay|\bxiis|awrbogays|biyagadu+d|carmaale|celayo|dibqarax|gudmo\W*biya\W*cas|hare+d|\bxi+s|c[ei]+gavo|ce+r[ai]?ga*b[0o]|ce+rig|dibqarax|hay\W*lan|ji+dali|lasasurad|maydh|xingalol|\byub+e|yufle|durdur|fiqi\W*filiye|fuqulfulye|\blaso|\bxi+[sz]\b|cargabo|ce+\W*ga+bo|ce+ribo|ceirgabo|her\W*ga+bo",
        SomaliaCodes.DHUUSAMARREEB: r"[dn]h*[ou]+\W*s[aeo]\W*ma+r+e+b|dh?u+sa?[bm]a?re+b|dumareb|dhusma?ru?b|dh?u+sa*mare*b|\bdhu+sa|dusa*ma+re+b|\bdusmo|\bmar+eb|dhusamare+b|dh\W*mar+e+b|[hx]arare|dh\su+s[ao]\s*ma?re+b|d(us)?\Wmare+b|dhu\s?o?ma?re+b|qurace+l|guraca+l|[gq]ur[aeiu]\W*c+e+l|dus?ma\W*re+[bv]|xanan\sbu+re|g\Wce+l|galajir|godinlabe|xanan\W*bu+re|dhuds mare+b|dosmoreb|gu?\W*r?i?\W*ceel|gu+rac+[eyl]+|gurcie+l|gurcl|gur[eu]\W*c?e+l|[kq]uri\W*ce+l|mare+r\W*gur|q[ou]re?ce+|\bgabu+n|\bgur\W*el|dhus\W*[mn]are+b",
        SomaliaCodes.DIINSOOR: r"di+n?i?\W*so+r",
        SomaliaCodes.DOOLOW: r"\bdo+l+o+w?",
        SomaliaCodes.EYL: r"\b[ae]yl\b|\bjal+a?m\b|\baal\b",
        SomaliaCodes.GAALKACYO: r"ga+l*ka+c+\s?yo|ka+lgac*yo|glkcy|gal[kc]aio|glkcyo*|ga[cl]kio|ga+l[gka]+c\W*[yv]o?|ga+l\s?kaciy?o|ka+lkacyo|ga+lkcayo|kalkacayo|baca+dway*n|balis*bus*le|bandi+radle+[iy]|ga+lkacayo|garso+r|galcaio|galkacyfo|glkacyo|gana+ne|glkaio|ma+rodijex|ga+l\skayco|galakcyo|galkay|\bglkio\b|kal\s?kacyo|galc(ak)?yo|gackio|quir\W*cel|glckyo|ga+l\W*kac\W*y|halabo+khad|\bxarfo|\bdocol|ga[lr]\W*so+r|[hx]arfo|ga+lkaio|qarqo+ra\sdhe+r|balanbal|glkayo|kalcayo|qarqo+ra\W*dhe+r|xa+fada?\W*falu+ja|g\W*kacyo|\bga+lkac|\bisra+c|ja+ndhe+r|\bsaaxo|xanan\W*bu+ro|qar\W*sooni|dhagax\W*yacado",
        SomaliaCodes.GALDOGOB: r"g[ao]ld[ao]gob|gar\sadag|\bgodob\b|goldogob|gudubi|dobogle|da+r[aou]p?\W*sala+[mn]|bursa+la?x|g\W*dogob|dalasan",
        SomaliaCodes.GARBAHAAREY: r"ga+rba+ha+r+[ae]+y|ba+ha+r[ae]y|garba+re+y|kalbar+e|ganbadha|barwa+qo|qorof|ce+l\W*cade|grbhrey",
        SomaliaCodes.GAROWE: r"g[oa]r[ao]+w*e|qarawe|groe|g\s?arow?e|gro+we?|casumada nugal|garo+i?w|garwe?|grawe|grwe|gararo+we|gorewe|cas[ai]mda\W*puntla?nd|shimbirale|darayle|jowle|garewe|gwre",
        SomaliaCodes.GEBILEY: r"g[ea]bi+l[ae]*y|gowale|al+[ae]?y\W*bada?y|a\W*rabsl?i?yo|ija+ra|agabar|agamsaha|ija+ra|be+yo\nW*li+ba+n|d\W*wajale|\bdil+a|duruqsi|gogol\W*wana+g|go+ba+la|lafta|rabsiy?o|wajale|ge+d\W*bala+dh|qabile|wa+lid\W*xo+r",
        SomaliaCodes.HARGEYSA: r"ha+[dr]a?\s?g[ae]+[yi]+a?s[ao]*|2[06]\W?(ka)?j[ou]+n|31\W*(ka)?\W*ma?y|62\W?ju+n|150|a([hx]\W*m[ae]d)?\W*d?(gha)+g[ahx]|axm[ae]d\W*guray|axmed(.*)haru+n|c\W*liba+x|caba+ye|cabdi\W*i+daan|[cg]a+[cgv,]a*n\s?lib?a+x|cala+mada|d\Wm\Whaybe|d\Wm\Wjeex|d\W+ko+d[ou]?b[au]+r|dhagax\see|g\Wli+ba+x|good\sbuur|gunbur\slibaax|hage[iy]sa|\bhar\b|harga+i?[sy]+(a|eis|pa)?|haragi+s|harge+r?[iyv]+si?a|hagesa|har+gesi?a?|hargi+[ey]?sa|hargsa|hargyia?s|harkeysa|hasgeis|\bhay\sb\b|hayaey|hragayas|\bhrg\b|hrgaysa|hrgsa|hrgwysa|hrgys|hrysa|i(br)?\W*ko+dbu+r|ibra+hi+[mn]\W*k[ou]*d\s?bu+[rq]|[jm]aro+di?\W*j[ae]+x|ko+\Wd\sbu+r|lu+q gana+ne|m\shaybe|m\Wmo+ge|m\Wha+ru+n|m\Wh[ae]ybe|m\Wje+x|m\W+x\W+haybe|maca+li+\Wharu+n|mahamoud\W*haybe|man?dhe+[qr]|ma[jr][0eou]+(d[ei]+)?\W*je*[dhx]|maroodi|maxaed haybe|ma?xa?m[aeou]*d\Wmo+ge|max\W*ed\W*mo+ge|m[aou][hx][am]*t*[aeou]+d(.*)ha?yi?b|m[ao][hx]a\W*mu+d\W*h[ae]?i?\W*be|mo+r[ao]di je+x|\bmrj\b|m(ax)?\W?u+d\W+haybe|qudhacdher|sabawana+g|salehlay|sh\Wmadar|sh\Wnu+r|sh\Wdhexe|shacabka|waabacado|war ida+d|xa+xi|xer[ao]+\s?[ao]?wr|cala+mada|dacar\sbudhuq|deeble|daloodho|\b26|\bm\.h\b|gargasa|har[ae]?g[ai]+sa|hargyza|hardeysa|haregaysa|hargeiza|hargysa|\b150|ahm[ae]d\W*dha?ga[hx]|abaarso|axmad\W*guray|faraw[ae]*y?ne|fara\W*wawyan|farawi+n|g\W*libah|[gq]a\W*c?an\W*liba+h|gacanli+ba+x|goryo|harge+sa|qudhac\Wdhe+r|xa+fada\W*m\W*mo+ge|a\W*dhagax|aba+rso|bala?[iy]\W*ca+ban|bal+i\W*mata+n|bal+igubadle|d\W*ib\W*ko+dbu+r|da+dley|balimata+n|la+s\W*ge+l|fara\W*w[ae]+w?y?ne|dhabo+laq|farawi+n|farlibax|g\W*liba+[hx]|ga+\W*c?an\W*li+ba|ge+d?\W*deble|gobdhe+r|godbur|goryo|gu[mn]buraha|h[ao]+rg?a?[iy][@@sz]a|harge+\W*i?sa|hars?[gy]e[iy]sa|ko+da?bu|jale+lo|jigjig(.*)ya|macalin\Wha+ru|qodax|qo+l\W*cada|qudhac\W*dhe|xa+fad(.*)mo+g|axmed+haga|xawa+dle|axa?m[ae]d\W*dhagax|faraw[ae]yi?n|bal+[ayi]+\W*caban|ax\W*medhagx|axmad\W*guray|a[xy]m[ae]?[df]\W*dha*(ga)?a*x|ko+d\W*bu+r|b(alay)?\W*cabane|bal+i\W*gubad\W*le|bi+bsiga|bili\W*cabane|boqol\W*iyo\W*kont[ao]nka|cada+dlay|casamad\W*marad\W*jax|ko+[dr]bu+r|dal+o+dho|[df]arar?wayne|slaxley|mxed\W*mooge|max\W*ed\W*haybe|maxamu+d\W*[bh]ay?[ae]*b?e|di+nqal|halayo|haraf|har[ai]ga?y?e?sa|h[ae]rg[ae]gays|hargeuisa|harg[iy]?e?s|hasgaysa|i[bp](.*)k[ou]+d?[bp]u|ina+\W*mo+ge|jig\W*jiga?\W*y|ji+ja\W*yr|kaw\W*iyo\W*sodon\W*may|\b\Wmh\b|m\W*ha[iy]be|macalin\W*ha+ru+n|man?dhe+[dhr]|maga+la\Wmadaxda\Wso+ma+liladn|malawle|mara+ga|masalaha|xaraf|axm[ae]d\W*dhaxa|axm[ae]*[df]\W*dha*[gq]a*x|balaygubadle|bilugubale|biya\W*shi+naha|a\W*dhagax|dacarbudhuq|ga?\W*[acx]*n\W*li+ba|garabis|m\W*dheera|sa+laxla+y|sala?[hx]a?\W*lay|she+daha|\btoon|u+ba+le|xa+fada\W*ca+baye|xa+fada\W*ida+cada|heybe|xa+fda\W*xa+ji\W*cu\W*mardiga+le|xafada\W*xawa+dle|xare+d|xe+r[ao]\W*a+w+a?r|\bmooge|harkeyso|sal+axl[ae]y|i\W*k\W*bur",
        SomaliaCodes.HOBYO: r"\bh[ao]byo|cama+ra|ce+l\W*gu+la|ji+cdhe+re|korodhi|t[ou]+w?\W*fi+[gq]",
        SomaliaCodes.ISKUSHUBAN: r"iskh*u+\W*shu+ban|gumbax|\bxa+fu+n|ba+r[gk]?[ae]*l|dharo+r|gargo+re",
        SomaliaCodes.JALALAQSI: r"jalal*a*qsi|jala\W*la?[pq]si",
        SomaliaCodes.JAMAAME: r"j[ai]m+a+m[ae]|jamamo|garacad|kamsu+ma|sangu+ni|turdho|jama+\W*mae|jamaamo|\bjamal\b|^\W*jma?\W*$",
        SomaliaCodes.JARIIBAN: r"j[eai]ri+ba+n|ja+ri*\W*[bmn]a*n|garacad|godobji+ran|jrbn",
        SomaliaCodes.JOWHAR: r"j[ao]+w*a?\W*h[ae]r|\bj[ou]+har\b|mahada+y|\bjo?wa?hr\b|\bjowha\b|\bhowhar\b|kaxarey|cadiga\W*mo+ble+n|deganka\W*kongo|\bgu+mar|\bjuhur|qalimo+w|afarta\W*tu+lo|biya\W*cade|celbaraf|\bjarirow|\bjow[ao]r|maquda+le|\buba+le|\bjahay\b|jawhar|\bjow\b|johwar",
        SomaliaCodes.JILIB: r"jili+[bm]|mare+rey",
        SomaliaCodes.KISMAYO: r"k[ia]s[ai]*\W*ma+yo*|kisma+n?w?\W*yo|\bkis*[mw]a*yo|go+bwayn|dalxi+ska|dalxi*s|go+bw[ea]yn|chisma[yi]o|ki?s\s?mayo|cabdi dh?oore|kisma*n?yo|cabdala\sbiro+le|qod\W*qod|be+rxa+n|bula?\W*gadu|cabdala\W*biro+le|dhasheg\W*wa+mo|qa+m\W*qa+m|qod\W*qod|kismo|alanley|be+r\W*xa+n|cabdi\W*dho+re|farjano|jana+\W*cabdala|kha+m\W*kha+m|kima+nyo|kismio|\bkisyo|\bksm\b|mayondo|xa+r\W*xa+r|ksma+yo|\bkis\b",
        SomaliaCodes.KURTUNWAAREY: r"kur*n*tu+n*wa+r[ae]y|kl?W*warey|klwarey|kunta\W*wa+rey|bu+lmare+r|daca+ro|kur[nt]un\W*wa+rey|k\W*warey",
        SomaliaCodes.LAAS_CAANOOD: r"la+sc*a+no+d|la+s\W*[ca]+a+no|la+sasurud|yeyle|kala?b[ae]+y|sa+xdhe+r|casu+ra|yeyle|las\W*nod|xa+ji\W*hi+rad",
        SomaliaCodes.LASQOORAY: r"la+shorey|la+s\W*qo+\W*ray|\b(la)*s*k\s*ho+rey*|badhan|dhahar|bu+ra+n|ce+la+yo|bo+da\W*cad|durduri|\bhilo|moholin|ulxe+d",
        SomaliaCodes.LUGHAYE: r"lugh*a[iy][ea]|carmale",
        SomaliaCodes.LUUQ: r"\blu+[qkg]h*|\blu+[pq]|degmadalu+\W*q",
        SomaliaCodes.MARKA: r"\bm[ae]+r[ck][oa]*\b|jana+le|bulo\W*mare+r|caga+ran|h[ou]r\W*se+d|sh l m b t|shalambo+",
        SomaliaCodes.OWDWEYNE: r"o+w?dw[ae]n*[iy]ne|o+w?dw[ae]+n*[iy][ei]n|da+d\W*madhe+dh|gatitaley|\bgo\W*o\b|owdwe+y?ne|xa+ji\W*sa+l+ax",
        SomaliaCodes.QANDALA: r"[qgk]a+n*a?\W*da+l+a|balidhidin|bilci+l|khandala",
        SomaliaCodes.QANSAX_DHEERE: r"qan*sah*\W*dh*e+re|[gq]an?sax\W*dhe+re|gansaxdhere|\bufuro|q[ao]n\W*sax\W*dhe+r|q\W*dhe+r",
        SomaliaCodes.QARDHO: r"[gqk]ara*dh*[ao]|dan\W+goroyo|d[ao]ngor[ao]?yo|qard*\s*d*h*o|qhardi|dan\W*go+royo|karka+r|qardh|rako\s(raxo|xaro)|she+rbi|xid+o|yaka|dalwayn|khardh?o|qardbo|rako\W*[rx]a+[rx]o|wa+ciye|xid+o|xa+jikhayr|dan\W*goranyo|dan\W*goroyo|dalwayn|\bkarka+r|kuubo|qaradho|qardbo|qardh|qargho|rako|\bshe+rbi|wa+ciy|xiddo|xumbays|\byaka|mayga+g|wa+\W*ciye",
        SomaliaCodes.QORYOOLEY: r"qo+r[iy]o+[iy]*l[ae]y|qorya+le|qor\W*yo+ley|farso+ley|jeerow|q[o0]yale|qorale+y|q[ou]r\W*yoo\W*le?y|qoyaale|tawakal",
        SomaliaCodes.RAB_DHUURE: r"\brab*\W*d*hu+re*\b|\byeed\b",
        SomaliaCodes.SAAKOW: r"sa+ko+w|\bdudun",
        SomaliaCodes.SABLAALE: r"sa+bl+a+le",
        SomaliaCodes.SHEIKH: r"\bshe+i*kh*\b|\bshiekh\b|warshakh|g\W*liba+x|ga\W*c*an\W*liba|gidheys|laalays|\bshiikh\b",
        SomaliaCodes.TALEEX: r"t[e    a]leh|taytayle+h|tal[iy]e|t[ea]le+x|tale+h|shaxda|car+o+ley",
        SomaliaCodes.TAYEEGLOW: r"te+glow|ti[jy]?[ae]+glo+w|taye+glow|tiyok\W*low",
        SomaliaCodes.WAAJID: r"\bwa+ji+d|wajaale",
        SomaliaCodes.WANLA_WEYN: r"wan*i?l[ae]\W*w[ae]+y*n|\bda+fe[dt]|walawe+nay|wanle\W*w[ae]+y?n",
        SomaliaCodes.XARARDHEERE: r"x*harar*\W*dh*e+re|xara[nr]*\W*dhe+[re]*|xi+ndhe+re|dabagalo|xrdhe+re|x\W*dhere",
        SomaliaCodes.XUDUN: r"[hx]u+du+n|gog\W*dhe+r|\bbohol|afurur|gog\W*dhe+r|ce+l\W*garas",
        SomaliaCodes.XUDUR: r"[hx]u+d+u+r|xa+ba+le|ce+l\W*garas",
        SomaliaCodes.ZEYLAC: r"ze[yi]la|zeylac|sa+[iy]la+c|xajizalax|sayla|ce+lga+l|\bdila\b|lawyocado|sayilac",
        SomaliaCodes.MOGADISHU: r"m[ou]+[gkq]a*d[yi]sh*x*[uo]|m[auo][qg][ua]*dh*[ui]sh[oa]|kuqdisho|mukh\sdisho|capital|casima*d|ca+s[iu]\W*mad|garas\W?baley|[kq]axda|xa+wo\W*ta+ko|b\Wxube+y|ba+r\subax|carafa+[dt]|madi+no|\bsanco|sonikey|su+[gq]a?\s?xo+l|warta\Wnaba?d+a|xasa\shila+c|b\W*xube+y|ba+r\W*ubax|bakaro|bo+la+|ceymiska|d\W*jazi+ra|c\W*cazi+z|si+na+y|w\W*beri|wrta\W*nabada|ge+d\W*jecel|ju+ngal|ka+wa\W*godey|\bkahda|km4|\b[hx]amar\b|liliwa|\bso+be|su+qa?\W*xo+l|war[dt]a\W*n[ao]+[bw]a?d|so+nikey|hila+c|xbsiga\W*dhexe|huqdisho|arjatin|b\W*xube+y|ba+r\W*ubax|baka+ro|bakaraha|\bbo+la|ceymiska|d\W*jazi+ra|d\W*w\*nabada|\bkxd|carafa+[dt]|wa?r[dt]a\W*nabada|exka+ntaro+l|fo+rilow|garas\W*ba+le|ge+d\W*j[ae]ce+l|gubadle+y|hamar\W*cade+y|ka+wa\W*godey|\bka[hx]d|ma?di+no|m[ao]g[ao]\W*disho|magodusha|modisho|muqdiysha|mu+qdisho|ra+de+lka|shi+rkole|siinka|so+n[ai]k[ae]y|\bsoobe|su+qa?\W*xo+l|tabelaha shiiq ibraahin|taredisho|war\W*ta\W*nawa+d|\bwarta|wo+lwada+g|x\W*we+ne|marjadi+d|xasa\W*hila+c|huqdisho|m[ou]\W*(p|q|kh)d[ei]\W*sh[ou]|magala\W*madaxa|mqdsho|mu[kq]\W*dish",
    }
