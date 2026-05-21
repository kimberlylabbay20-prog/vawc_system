(function () {
  'use strict';

  /* ============================================
     VAWC ASSISTANT — FAQ + Chatbot
     ============================================ */

  const ASSISTANT_CSS_ID = 'vawcAssistantStyle';
  const FAB_ID = 'vawcAssistantFab';
  const OVERLAY_ID = 'vawcAssistantOverlay';
  const CLOSE_ID = 'vawcAssistantClose';
  const FAQ_CONTAINER_ID = 'vawcAssistantFaq';
  const CHAT_MESSAGES_ID = 'vawcChatMessages';
  const CHAT_INPUT_ID = 'vawcChatInput';
  const CHAT_SEND_ID = 'vawcChatSend';

  let overlay, fab, closeBtn, chatMessages, chatInput, chatSend;

  /* ============================================
     FAQ DATA
     ============================================ */
  const vawcFaqData = [
    {
      q: 'Why is reporting VAWC important?',
      a: 'Reporting VAWC is crucial because it helps stop the abuse, protects potential future victims, and holds abusers accountable. Your report can be the first step toward justice and healing — not just for yourself, but for others in your community who may be suffering in silence.'
    },
    {
      q: 'What happens if I stay silent?',
      a: 'Staying silent may allow the abuse to continue or escalate, endangering your safety and well-being. Abuse rarely stops on its own — it often worsens over time. Speaking up, even step by step, opens the door to protection, support, and recovery. You are not alone.'
    },
    {
      q: 'Can VAWC affect mental health?',
      a: 'Yes, VAWC can have serious effects on mental health, including anxiety, depression, post-traumatic stress disorder (PTSD), low self-esteem, and suicidal thoughts. Emotional and psychological wounds can be as deep as physical ones. Seeking help is a sign of strength, not weakness.'
    },
    {
      q: 'Is reporting confidential?',
      a: 'Yes. Your report and identity are kept confidential under Philippine law (RA 9262 and other statutes). Barangay officials, police, and social workers are required to protect your privacy. Your information will only be shared with authorized personnel handling your case.'
    },
    {
      q: 'Can minors report abuse?',
      a: 'Yes, minors can report abuse. They may file a report on their own or with the help of a parent, guardian, teacher, or any trusted adult. The DSWD and barangay are required to take immediate action to protect the child. No child should suffer in silence.'
    },
    {
      q: 'What kinds of abuse are considered VAWC?',
      a: 'VAWC covers physical abuse (hitting, slapping, kicking), psychological/emotional abuse (threats, intimidation, gaslighting), sexual abuse (rape, coercion, unwanted acts), economic abuse (withholding financial support, controlling resources), and stalking or harassment.'
    },
    {
      q: 'How can barangays help victims?',
      a: 'Barangays are the first line of defense. They can issue Barangay Protection Orders (BPO), conduct mediation (in appropriate cases), refer victims to social workers, provide temporary shelter, and coordinate with PNP and DSWD for further assistance.'
    },
    {
      q: 'What legal rights do victims have?',
      a: 'Victims have the right to protection orders (BPO, TPO, PPO), free legal assistance from PAO, medical treatment and counseling, confidentiality, temporary shelter, and to pursue criminal, civil, or administrative cases against the abuser.'
    },
    {
      q: 'Can emotional abuse be reported?',
      a: 'Yes, emotional and psychological abuse are explicitly recognized under RA 9262. Acts like threats, intimidation, humiliation, controlling behavior, and verbal abuse are punishable by law. You have the right to report emotional abuse and seek protection.'
    },
    {
      q: 'Where can victims get support?',
      a: 'Victims can get support from their Barangay VAWC Desk, PNP Women and Children Protection Desk (WCPD), DSWD (crisis intervention and shelter), Public Attorney\'s Office (free legal aid), and local women\'s organizations. In emergencies, call 911.'
    }
  ];

  /* ============================================
     CHATBOT KNOWLEDGE BASE
     ============================================ */
  const vawcKnowledgeBase = [
    {
      keywords: ['report', 'reporting', 'file', 'submit', 'how to report', 'magreport', 'mag-ulat', 'isumbong', 'sumbong', 'ireport', 'magreport'],
      response: 'To report VAWC, you can go to your barangay hall and speak with the VAWC Desk officer, visit the nearest PNP Women and Children Protection Desk (WCPD), or contact DSWD. You may also file a report through this online form. All reports are kept confidential.',
      response_tl: 'Para mag-report ng VAWC, pwede kang pumunta sa barangay hall at makipag-usap sa VAWC Desk officer, pumunta sa pinakamalapit na PNP Women and Children Protection Desk (WCPD), o tumawag sa DSWD. Pwede ka ring mag-report gamit ang online form na ito. Lahat ng report ay confidential at ligtas.'
    },
    {
      keywords: ['abuse', 'abusive', 'abused', 'hurt', 'hit', 'beat', 'abuso', 'inaabuso', 'sinasaktan', 'nasasaktan', 'saktan', 'sinaktan'],
      response: 'Abuse is never your fault. Whether physical, emotional, sexual, or economic — you deserve to be safe. VAWC cases can be reported to your barangay, PNP WCPD, or DSWD. Help is available, and you have legal rights to protection.',
      response_tl: 'Hindi mo kasalanan ang pang-aabuso na nararanasan mo. Kahit ito ay physical, emotional, sexual, o economic abuse — nararapat kang maging ligtas. Ang mga kasong VAWC ay pwedeng i-report sa iyong barangay, PNP WCPD, o DSWD. Nariyan ang tulong, at may karapatan kang maprotektahan.'
    },
    {
      keywords: ['violence', 'violent', 'karahasan', 'marahas', 'violenteng'],
      response: 'Violence in any form is not acceptable. Under RA 9262, acts of physical, sexual, psychological, and economic violence against women and children are punishable by law. If you are experiencing violence, please reach out to your barangay or call 911 in emergencies.',
      response_tl: 'Ang karahasan sa anumang anyo ay hindi katanggap-tanggap. Sa ilalim ng RA 9262, ang physical, sexual, psychological, at economic violence laban sa kababaihan at bata ay may parusa sa batas. Kung nakakaranas ka ng karahasan, mangyaring makipag-ugnayan sa iyong barangay o tumawag sa 911 kung emergency.'
    },
    {
      keywords: ['mental health', 'anxiety', 'depression', 'trauma', 'stress', 'counseling', 'mental', 'mental na'],
      response: 'VAWC can cause deep emotional and psychological wounds. You deserve mental health support — counseling is available through DSWD, local health centers, and women\'s organizations. Taking care of your mental health is a vital part of healing.',
      response_tl: 'Ang VAWC ay maaaring magdulot ng malalim na emosyonal at sikolohikal na sugat. Karapat-dapat kang humingi ng suporta para sa iyong mental health — available ang counseling sa pamamagitan ng DSWD, local health centers, at mga organisasyon ng kababaihan. Ang pag-aalaga sa iyong mental health ay mahalagang bahagi ng paggaling.'
    },
    {
      keywords: ['legal', 'rights', 'law', 'lawyer', 'attorney', 'court', 'case', 'karapatan', 'abogado', 'pao', 'demanda', 'kasuhan'],
      response: 'Victims of VAWC have rights under Philippine law: the right to protection orders (BPO/TPO/PPO), free legal assistance from the Public Attorney\'s Office (PAO), confidentiality, and the right to pursue legal action against the abuser. You do not need a lawyer to start — barangay officials can assist you.',
      response_tl: 'Ang mga biktima ng VAWC ay may mga karapatan sa ilalim ng batas ng Pilipinas: karapatan sa protection orders (BPO/TPO/PPO), libreng legal na tulong mula sa Public Attorney\'s Office (PAO), confidentiality, at karapatang magsampa ng kaso laban sa nang-aabuso. Hindi mo kailangan ng abogado para magsimula — tutulungan ka ng barangay.'
    },
    {
      keywords: ['protection', 'protection order', 'bpo', 'tpo', 'ppo', 'safe', 'safety', 'proteksyon', 'protekahan', 'protektado'],
      response: 'Protection orders are legal documents that prohibit the abuser from harming or approaching you. Barangay Protection Orders (BPO) are issued by the barangay and take effect immediately. Temporary (TPO) and Permanent (PPO) Protection Orders are issued by the court.',
      response_tl: 'Ang protection order ay legal na dokumento na nagbabawal sa nang-aabuso na saktan o lapitan ka. Ang Barangay Protection Order (BPO) ay ibinibigay ng barangay at agad na may bisa. Ang Temporary (TPO) at Permanent (PPO) Protection Orders ay ibinibigay ng korte.'
    },
    {
      keywords: ['barangay', 'barangay help', 'kagawad', 'lupon', 'kapitan', 'barangay hall', 'barangay'],
      response: 'Your barangay is your first step. Visit the Barangay VAWC Desk and ask for a Barangay Protection Order (BPO) if you are in danger. Barangay officials can also refer you to DSWD, PNP, and other agencies for further support and shelter.',
      response_tl: 'Ang iyong barangay ang unang hakbang. Pumunta sa Barangay VAWC Desk at humingi ng Barangay Protection Order (BPO) kung ikaw ay nasa panganib. Ang mga opisyal ng barangay ay maaari ring mag-refer sa iyo sa DSWD, PNP, at iba pang ahensya para sa karagdagang suporta at masisilungan.'
    },
    {
      keywords: ['emergency', 'urgent', 'danger', '911', 'immediate', 'help now', 'saklolo', 'emergency', 'delikado'],
      response: 'If you are in immediate danger, call 911 or go to your nearest barangay hall or police station right away. Do not wait. Your safety is the top priority. You can also contact PNP WCPD at 0919-777-7377 for 24/7 assistance.',
      response_tl: 'Kung ikaw ay nasa agarang panganib, tumawag sa 911 o pumunta agad sa pinakamalapit na barangay hall o police station. Huwag maghintay. Ang iyong kaligtasan ang pinakamahalaga. Pwede ka ring tumawag sa PNP WCPD sa 0919-777-7377 para sa 24/7 na tulong.'
    },
    {
      keywords: ['women', 'woman', 'kababaihan', 'babae', 'kababaihan'],
      response: 'Women have the right to live free from violence and fear. RA 9262 specifically protects women and their children from all forms of abuse. You have access to legal aid, medical support, counseling, and shelter. You are not alone — help is here.',
      response_tl: 'Ang mga kababaihan ay may karapatang mabuhay nang walang karahasan at takot. Ang RA 9262 ay espesyal na nagpoprotekta sa mga kababaihan at kanilang mga anak laban sa lahat ng uri ng pang-aabuso. May access ka sa legal aid, medical support, counseling, at shelter. Hindi ka nag-iisa — nariyan ang tulong.'
    },
    {
      keywords: ['children', 'child', 'minor', 'bata', 'kids', 'anak', 'bata', 'bantan'],
      response: 'Children have special protection under Philippine law. RA 9262 and the Child Protection Law (RA 7610) safeguard minors from abuse, neglect, and exploitation. Minors can report abuse with or without a guardian. DSWD provides immediate intervention and care.',
      response_tl: 'Ang mga bata ay may espesyal na proteksyon sa ilalim ng batas ng Pilipinas. Ang RA 9262 at Child Protection Law (RA 7610) ay nagpoprotekta sa mga menor de edad laban sa pang-aabuso, pagpapabaya, at pagsasamantala. Pwedeng mag-report ang mga bata kahit walang kasamang magulang. Ang DSWD ay nagbibigay ng agarang tulong at pangangalaga.'
    },
    {
      keywords: ['emotional abuse', 'psychological', 'verbal', 'gaslighting', 'manipulation', 'damdamin', 'emotional', 'pananakit ng damdamin', 'verbal abuse'],
      response: 'Emotional and psychological abuse is real and punishable under RA 9262. This includes threats, intimidation, humiliation, verbal attacks, and controlling behavior. You have the right to report emotional abuse and seek protection and counseling.',
      response_tl: 'Ang emotional at psychological abuse ay totoo at may parusa sa ilalim ng RA 9262. Kasama rito ang pananakot, pambu-bully, pagpapahiya, verbal attacks, at pagkontrol. May karapatan kang mag-report ng emotional abuse at humingi ng proteksyon at counseling.'
    },
    {
      keywords: ['physical abuse', 'physical', 'hitting', 'slapping', 'kicking', 'injured', 'pananakit', 'suntok', 'sipa', 'sabunot', 'nasaktan', 'physical na'],
      response: 'Physical abuse is a serious offense under RA 9262. If you have been physically harmed, seek medical attention immediately at any government hospital (you are entitled to free treatment). Report the incident to your barangay or the police.',
      response_tl: 'Ang physical abuse ay malubhang kaso sa ilalim ng RA 9262. Kung ikaw ay sinaktan nang pisikal, agad na humingi ng medical attention sa anumang government hospital (may karapatan kang libreng gamutan). I-report ang insidente sa iyong barangay o sa pulisya.'
    },
    {
      keywords: ['harassment', 'stalking', 'bastos', 'catcalling', 'harass', 'bastosin', 'binabastos', 'pananakot'],
      response: 'Harassment and stalking are prohibited under the Safe Spaces Act (RA 11313) and RA 9262. This includes unwanted advances, following, catcalling, and online harassment. You can report these incidents to your barangay or the PNP WCPD.',
      response_tl: 'Ang harassment at stalking ay ipinagbabawal sa ilalim ng Safe Spaces Act (RA 11313) at RA 9262. Kasama rito ang hindi gustong advances, pagsunod, catcalling, at online harassment. Pwede mong i-report ang mga ito sa iyong barangay o sa PNP WCPD.'
    },
    {
      keywords: ['confidential', 'confidentiality', 'private', 'identity', 'secret', 'anonymous', 'lihim', 'seguridad', 'anonymous'],
      response: 'Your report and identity are confidential under Philippine law. Barangay officials, police, and social workers are legally required to keep your information private. It is only shared with authorized personnel handling your case.',
      response_tl: 'Ang iyong report at pagkakakilanlan ay confidential sa ilalim ng batas ng Pilipinas. Ang mga opisyal ng barangay, pulis, at social worker ay legal na kinakailangan na panatilihing pribado ang iyong impormasyon. Ito ay ibinabahagi lamang sa mga awtorisadong tauhan na humahawak ng iyong kaso.'
    },
    {
      keywords: ['shelter', 'tirahan', 'evacuate', 'stay', 'safe house', 'ligtas', 'ligtas na lugar', 'masisilungan'],
      response: 'If you need a safe place to stay, DSWD provides temporary shelter and psychosocial support. Your barangay can help coordinate transportation and referral. You do not need to stay in an unsafe environment — help is available.',
      response_tl: 'Kung kailangan mo ng ligtas na matutuluyan, ang DSWD ay nagbibigay ng temporary shelter at psychosocial support. Ang iyong barangay ay makakatulong sa transportasyon at referral. Hindi mo kailangang manatili sa hindi ligtas na lugar — may tulong na naghihintay sa iyo.'
    },
    {
      keywords: ['financial', 'economic', 'money', 'support', 'sustento', 'child support', 'pera', 'pinansyal', 'financial abuse'],
      response: 'Economic abuse — such as withholding financial support, controlling all money, or preventing you from working — is recognized under RA 9262. You have the right to financial support for yourself and your children. The court can order support payments.',
      response_tl: 'Ang economic abuse — tulad ng pagpigil ng financial support, pagkontrol sa lahat ng pera, o pagbawal sa iyo na magtrabaho — ay kinikilala sa ilalim ng RA 9262. May karapatan kang tumanggap ng financial support para sa iyong sarili at sa iyong mga anak. Ang korte ay maaaring mag-utos ng sustento.'
    },
    {
      keywords: ['natatakot', 'takot', 'scared', 'fear', 'frightened', 'afraid', 'nerbiyos', 'anxious', 'worried', 'nakakatakot'],
      response: 'It is completely normal to feel afraid. You are not alone, and there are people who can help you. Your safety matters. Please reach out to your barangay, a trusted friend, or a support hotline. You deserve to feel safe.',
      response_tl: 'Normal lang na makaramdam ng takot. Hindi ka nag-iisa, at may mga taong handang tumulong sa iyo. Mahalaga ang iyong kaligtasan. Mangyaring makipag-ugnayan sa iyong barangay, sa pinagkakatiwalaang kaibigan, o sa support hotline. Karapat-dapat kang maging ligtas at payapa.'
    },
    {
      keywords: ['ano gagawin', 'what to do', 'paano', 'gawin', 'gagawin', 'saan', 'san ako', 'paano ba', 'ano ang', 'ano pwede'],
      response: 'Here are the steps you can take: 1) If in immediate danger, call 911 or go to your barangay. 2) Visit the Barangay VAWC Desk for assistance. 3) You may file a BPO (Barangay Protection Order). 4) Contact DSWD or PNP WCPD for further help. 5) Do not blame yourself — you deserve support.',
      response_tl: 'Narito ang mga hakbang na pwede mong gawin: 1) Kung nasa panganib, tumawag sa 911 o pumunta sa barangay. 2) Pumunta sa Barangay VAWC Desk para sa tulong. 3) Pwede kang humingi ng BPO (Barangay Protection Order). 4) Tawagan ang DSWD o PNP WCPD para sa karagdagang tulong. 5) Huwag sisihin ang iyong sarili — karapat-dapat kang tumanggap ng suporta.'
    },
    {
      keywords: ['pwede bang anonymous', 'anonymous', 'hindi magpakilala', 'secret', 'hindi malalaman', 'incognito', 'anonymous report'],
      response: 'Yes, you can make an anonymous report. While providing your identity helps authorities follow up on your case, you may still report without revealing your name. Barangay and government agencies are required to keep all information confidential.',
      response_tl: 'Oo, pwede kang mag-report nang hindi nagpapakilala. Bagama\'t makakatulong ang iyong pagkakakilanlan sa pagsunod sa iyong kaso, pwede ka pa ring mag-report nang hindi ibinubunyag ang iyong pangalan. Ang barangay at mga ahensya ng gobyerno ay kinakailangang panatilihing confidential ang lahat ng impormasyon.'
    },
    {
      keywords: ['minor', 'bata', 'child', 'children', 'underage', 'menor de edad', 'magreport', 'pwede ba minor'],
      response: 'Yes, minors can report abuse. You can file a report on your own or with the help of a parent, guardian, teacher, or any trusted adult. The DSWD and barangay are required to take immediate action to protect the child. No child should suffer in silence.',
      response_tl: 'Oo, pwede mag-report ang mga menor de edad. Pwede kang maghain ng report mag-isa o sa tulong ng magulang, guardian, guro, o sinumang pinagkakatiwalaang adulto. Ang DSWD at barangay ay kinakailangang kumilos agad upang protektahan ang bata. Walang bata ang dapat magdusa nang tahimik.'
    },
    {
      keywords: ['kinokontrol', 'control', 'controlling', 'pagkontrol', 'pinaghihigpitan', 'pinagbabawalan', 'ginogoyo', 'manipulate', 'minamanipula'],
      response: 'Controlling behavior is a form of psychological abuse under RA 9262. This includes restricting your freedom, isolating you from family and friends, monitoring your movements, and making all decisions for you. You have the right to your own freedom and autonomy.',
      response_tl: 'Ang pagkontrol ay isang uri ng psychological abuse sa ilalim ng RA 9262. Kasama rito ang pagpigil sa iyong kalayaan, paghihiwalay sa iyo sa pamilya at kaibigan, pagmamanman sa iyong galaw, at paggawa ng lahat ng desisyon para sa iyo. May karapatan ka sa iyong sariling kalayaan.'
    },
    {
      keywords: ['pinagbabantaan', 'threat', 'threats', 'pananakot', 'binantaan', 'threaten', 'threatening', 'manakot', 'pinagbantaan'],
      response: 'Threats are a serious form of abuse under RA 9262. If someone is threatening you or your loved ones, you can report this to your barangay and request a Barangay Protection Order (BPO) immediately. Threats of harm are punishable by law.',
      response_tl: 'Ang pananakot ay malubhang uri ng pang-aabuso sa ilalim ng RA 9262. Kung may nananakot sa iyo o sa iyong mga mahal sa buhay, pwede mo itong i-report sa barangay at humingi agad ng Barangay Protection Order (BPO). Ang mga banta ng pananakit ay may parusa sa batas.'
    },
    {
      keywords: ['emotional support', 'support', 'kailangan ko ng tulong', 'tulong', 'help', 'malungkot', 'sad', 'lonely', 'depressed', 'depress', 'lungkot'],
      response: 'You are not alone. There are people who care and want to help you. You can reach out to DSWD for psychosocial support, talk to a trusted friend or family member, or contact a local women\'s organization. Your feelings are valid, and you deserve to be heard.',
      response_tl: 'Hindi ka nag-iisa. May mga taong nagmamalasakit at gustong tumulong sa iyo. Pwede kang makipag-ugnayan sa DSWD para sa psychosocial support, makipag-usap sa pinagkakatiwalaang kaibigan o kapamilya, o tumawag sa lokal na organisasyon ng kababaihan. Mahalaga ang iyong nararamdaman, at karapat-dapat kang pakinggan.'
    },
    {
      keywords: ['bawal', 'pwedeng', 'puede', 'pwede', 'alam', 'gusto', 'gustong', 'nais', 'nais kong'],
      response: 'I\'m here to help you with any VAWC concern. You can ask me about reporting abuse, protection orders, your legal rights, barangay assistance, emergency help, emotional support, and more. How can I assist you today?',
      response_tl: 'Nandito ako para tulungan ka sa anumang alalahanin tungkol sa VAWC. Pwede kang magtanong tungkol sa pag-report ng pang-aabuso, protection orders, iyong mga legal na karapatan, tulong ng barangay, emergency, emotional support, at iba pa. Paano kita matutulungan ngayon?'
    }
  ];

  const vawcDefaultResponse = 'I\'m here to help regarding VAWC concerns. Please try asking about reporting, abuse, legal rights, protection, or victim support.';
  const vawcDefaultResponseTL = 'Nandito ako para tumulong sa mga tanong tungkol sa VAWC. Pwede kang magtanong tungkol sa pag-report, pang-aabuso, legal na karapatan, proteksyon, o suporta para sa biktima.';

  /* ============================================
     LANGUAGE DETECTION
     ============================================ */
  function vawcDetectLanguage(msg) {
    const lower = msg.toLowerCase().trim();
    const tagalogIndicators = [
      'ako', 'ikaw', 'siya', 'sila', 'kayo', 'kami', 'tayo',
      'po', 'opo', 'oo', 'hindi', 'wala', 'meron', 'mayroon',
      'pwede', 'puede', 'ano', 'saan', 'bakit', 'paano', 'kailan', 'sino', 'magkano',
      'ang', 'ng', 'sa', 'ay', 'at', 'pero', 'kasi', 'dahil',
      'na', 'pa', 'din', 'rin', 'naman', 'lang', 'ba', 'ga', 'mga',
      'may', 'walang', 'huwag', 'wag', 'ito', 'iyan', 'yan', 'yun', 'dito', 'doon',
      'natatakot', 'takot', 'abuso', 'inaabuso', 'sinasaktan', 'saktan', 'sinaktan',
      'magreport', 'sumbong', 'isumbong', 'gagawin', 'kinokontrol', 'pinagbabantaan',
      'babae', 'bata', 'tulong', 'saklolo', 'barangay', 'kapitan', 'kagawad',
      'karapatan', 'abogado', 'sustento', 'tirahan', 'ligtas', 'sabi', 'kwento',
      'pamilya', 'anak', 'nanay', 'tatay', 'ina', 'ama', 'bahay', 'kapitbahay',
      'pulis', 'presinto', 'ospital', 'doctor', 'gamot', 'salamat', 'paalam',
      'nakakatakot', 'nerbiyos', 'stress', 'malungkot', 'lungkot',
      'gusto', 'gustong', 'nais', 'alam', 'intindi', 'unawa',
      'hiwalay', 'iwan', 'iniwan', 'asawa', 'dating', 'boyfriend', 'girlfriend',
      'karelasyon', 'partner', 'mura', 'sigaw', 'sinigawan', 'suntok', 'sipa',
      'kasuhan', 'demanda', 'reklamo', 'proteksyon', 'protekahan',
      'bastos', 'bastosin', 'binabastos', 'catcalling', 'bawal', 'pumunta'
    ];

    let score = 0;
    for (const word of tagalogIndicators) {
      const regex = new RegExp('\\b' + word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'i');
      if (regex.test(lower)) {
        score += 1;
      }
    }

    const tagalogStarters = ['pwede ba', 'ano ang', 'paano', 'bakit', 'saan', 'sino', 'gaano',
      'mayroon ba', 'meron ba', 'wala bang', 'hindi ba', 'paano ba', 'ano ba', 'pwede bang'];
    for (const starter of tagalogStarters) {
      if (lower.startsWith(starter)) {
        score += 2;
        break;
      }
    }

    return score >= 2 ? 'tl' : 'en';
  }

  /* ============================================
     CHATBOT LOGIC
     ============================================ */
  function vawcGetBotResponse(userMessage) {
    const msg = userMessage.toLowerCase().trim();
    if (!msg) return vawcDefaultResponse;

    const lang = vawcDetectLanguage(msg);

    let bestMatch = null;
    let bestScore = 0;

    for (const entry of vawcKnowledgeBase) {
      for (const kw of entry.keywords) {
        if (msg.includes(kw)) {
          const score = kw.length;
          if (score > bestScore) {
            bestScore = score;
            bestMatch = lang === 'tl' ? (entry.response_tl || entry.response) : entry.response;
          }
        }
      }
    }

    if (bestMatch) return bestMatch;
    return lang === 'tl' ? vawcDefaultResponseTL : vawcDefaultResponse;
  }

  /* ============================================
     TIMESTAMP
     ============================================ */
  function vawcGetTimestamp() {
    const now = new Date();
    let h = now.getHours();
    const m = String(now.getMinutes()).padStart(2, '0');
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return h + ':' + m + ' ' + ampm;
  }

  /* ============================================
     CHAT UI
     ============================================ */
  function vawcAddMessage(text, sender) {
    const div = document.createElement('div');
    div.className = 'vawc-chat-message ' + sender;

    if (sender === 'assistant') {
      const avatar = document.createElement('div');
      avatar.className = 'vawc-msg-avatar';
      avatar.innerHTML = '<i class="fas fa-robot"></i>';
      div.appendChild(avatar);

      const content = document.createElement('div');
      content.className = 'vawc-msg-content';

      const bubble = document.createElement('div');
      bubble.className = 'vawc-msg-bubble';
      bubble.textContent = text;
      content.appendChild(bubble);

      const time = document.createElement('div');
      time.className = 'vawc-msg-time';
      time.textContent = vawcGetTimestamp();
      content.appendChild(time);

      div.appendChild(content);
    } else {
      const content = document.createElement('div');
      content.className = 'vawc-msg-content';

      const bubble = document.createElement('div');
      bubble.className = 'vawc-msg-bubble';
      bubble.textContent = text;
      content.appendChild(bubble);

      const time = document.createElement('div');
      time.className = 'vawc-msg-time';
      time.textContent = vawcGetTimestamp();
      content.appendChild(time);

      div.appendChild(content);
    }

    chatMessages.appendChild(div);
    vawcScrollChat();
  }

  function vawcScrollChat() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function vawcShowTyping() {
    const typing = document.createElement('div');
    typing.className = 'vawc-typing';
    typing.id = 'vawcTypingIndicator';
    typing.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(typing);
    vawcScrollChat();
  }

  function vawcHideTyping() {
    const el = document.getElementById('vawcTypingIndicator');
    if (el) el.remove();
  }

  function vawcHandleSend() {
    const text = chatInput.value.trim();
    if (!text) return;

    vawcAddMessage(text, 'user');
    chatInput.value = '';
    chatSend.disabled = true;

    vawcShowTyping();

    setTimeout(function () {
      vawcHideTyping();
      const reply = vawcGetBotResponse(text);
      vawcAddMessage(reply, 'assistant');
      chatSend.disabled = false;
      chatInput.focus();
    }, 800 + Math.random() * 700);
  }

  /* ============================================
     FAQ LOGIC
     ============================================ */
  function vawcBuildFaq() {
    const container = document.getElementById(FAQ_CONTAINER_ID);
    if (!container) return;

    vawcFaqData.forEach(function (item) {
      const el = document.createElement('div');
      el.className = 'vawc-faq-item';

      const qEl = document.createElement('div');
      qEl.className = 'vawc-faq-question';
      qEl.textContent = item.q;

      const aEl = document.createElement('div');
      aEl.className = 'vawc-faq-answer';
      aEl.textContent = item.a;

      el.appendChild(qEl);
      el.appendChild(aEl);

      el.addEventListener('click', function () {
        const wasActive = el.classList.contains('active');
        // close all
        container.querySelectorAll('.vawc-faq-item.active').forEach(function (other) {
          other.classList.remove('active');
        });
        if (!wasActive) {
          el.classList.add('active');
        }
      });

      container.appendChild(el);
    });
  }

  /* ============================================
     GREETING
     ============================================ */
  function vawcSendGreeting() {
    setTimeout(function () {
      const greetings = [
        'Hello! I\'m your VAWC Assistant. Maaari kang magtanong tungkol sa VAWC, reporting, safety, legal rights, at victim support. Paano kita matutulungan ngayon?',
        'Hi! Ako ang iyong VAWC Assistant. You can ask me about reporting abuse, protection orders, your rights, or where to get help. Ano ang kailangan mong malaman?',
        'Welcome! I\'m here to help you. Pwede kang magtanong tungkol sa VAWC, pag-report, legal rights, protection, at emotional support. Huwag kang mahiyang magtanong.',
        'Hello there. You are not alone. I can help you with information about VAWC, barangay assistance, emergency contacts, and your legal rights. Ano ang gusto mong itanong?'
      ];
      vawcAddMessage(greetings[Math.floor(Math.random() * greetings.length)], 'assistant');
    }, 500);
  }

  /* ============================================
     OPEN / CLOSE
     ============================================ */
  function vawcOpen() {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    vawcScrollChat();
    chatInput.focus();
  }

  function vawcClose() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  /* ============================================
     INIT
     ============================================ */
  function init() {
    fab = document.getElementById(FAB_ID);
    overlay = document.getElementById(OVERLAY_ID);
    closeBtn = document.getElementById(CLOSE_ID);
    chatMessages = document.getElementById(CHAT_MESSAGES_ID);
    chatInput = document.getElementById(CHAT_INPUT_ID);
    chatSend = document.getElementById(CHAT_SEND_ID);

    if (!fab || !overlay || !chatMessages || !chatInput || !chatSend) return;

    // Build FAQ
    vawcBuildFaq();

    // Open
    fab.addEventListener('click', vawcOpen);

    // Close
    if (closeBtn) {
      closeBtn.addEventListener('click', vawcClose);
    }

    // Overlay click to close
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) vawcClose();
    });

    // Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('active')) {
        vawcClose();
      }
    });

    // Send on click
    chatSend.addEventListener('click', vawcHandleSend);

    // Send on Enter
    chatInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        vawcHandleSend();
      }
    });

    // Greeting
    vawcSendGreeting();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

/* ============================================
   DASHBOARD VAWC ASSISTANT FUNCTIONS
   Global — used by dashboard.html inline script
   ============================================ */

var DASH_LANG = 'en';

var DASH_FAQ_DATA = [
  {
    q_en: 'Why should I report if I am a VAWC victim?',
    q_tl: 'Bakit kailangan mag-report kung biktima ng VAWC?',
    a_en: 'Reporting VAWC is crucial because it helps stop the abuse, protects potential future victims, and holds abusers accountable. Your report can be the first step toward justice and healing — not just for yourself, but for others in your community who may be suffering in silence. You have the right to protection and support.',
    a_tl: 'Mahalaga ang mag-report ng VAWC dahil nakakatulong ito na matigil ang pang-aabuso, maprotektahan ang iba pang posibleng biktima, at managot ang nang-aabuso. Ang iyong report ay maaaring unang hakbang tungo sa katarungan at paggaling — hindi lang para sa iyo, kundi para sa iba sa iyong komunidad na tahimik na nagdurusa. May karapatan kang maprotektahan at makakuha ng suporta.'
  },
  {
    q_en: 'What is VAWC?',
    q_tl: 'Ano ang VAWC?',
    a_en: 'VAWC stands for Violence Against Women and Children. It refers to any act of gender-based violence that results in physical, sexual, psychological, or economic harm to women and children. This includes battery, threats, harassment, emotional abuse, economic control, and stalking. Under RA 9262, these acts are punishable by law.',
    a_tl: 'Ang VAWC ay Violence Against Women and Children o Karahasan Laban sa Kababaihan at Mga Bata. Ito ay tumutukoy sa anumang gawaing may karahasan na nagdudulot ng physical, sexual, psychological, o economic na pinsala sa kababaihan at bata. Kasama rito ang pananakit, pananakot, harassment, emotional abuse, pagkontrol, at stalking. Sa ilalim ng RA 9262, ang mga gawaing ito ay may parusa sa batas.'
  },
  {
    q_en: 'Is reporting confidential?',
    q_tl: 'Confidential ba ang pag-report?',
    a_en: 'Yes. Your report and identity are kept confidential under Philippine law (RA 9262 and other statutes). Barangay officials, police, and social workers are required to protect your privacy. Your information will only be shared with authorized personnel handling your case.',
    a_tl: 'Oo. Ang iyong report at pagkakakilanlan ay mananatiling confidential sa ilalim ng batas ng Pilipinas (RA 9262 at iba pang batas). Ang mga opisyal ng barangay, pulis, at social worker ay kinakailangang protektahan ang iyong privacy. Ang iyong impormasyon ay ibabahagi lamang sa mga awtorisadong tauhan na humahawak ng iyong kaso.'
  },
  {
    q_en: 'What support can I get?',
    q_tl: 'Anong tulong ang makukuha ko?',
    a_en: 'Victims of VAWC can get: (1) Protection Orders (BPO/TPO/PPO) to stop the abuser, (2) Free legal assistance from the Public Attorney\'s Office (PAO), (3) Medical treatment and counseling from government hospitals and DSWD, (4) Temporary shelter from DSWD, (5) Barangay assistance and referral to other agencies. In emergencies, call 911.',
    a_tl: 'Ang mga biktima ng VAWC ay makakakuha ng: (1) Protection Orders (BPO/TPO/PPO) para mapigilan ang nang-aabuso, (2) Libreng legal na tulong mula sa Public Attorney\'s Office (PAO), (3) Medical treatment at counseling mula sa government hospitals at DSWD, (4) Temporary shelter mula sa DSWD, (5) Tulong ng barangay at referral sa ibang ahensya. Sa emergency, tumawag sa 911.'
  }
];

/* ---------- TOGGLE POPUP ---------- */
function toggleVAWCAssistant() {
  var popup = document.getElementById('dashAssistantPopup');
  var fab = document.getElementById('dashAssistantFab');
  if (!popup || !fab) return;
  popup.classList.toggle('active');
  if (popup.classList.contains('active')) {
    setTimeout(function() { document.getElementById('dashChatInput').focus(); }, 400);
  }
}

/* ---------- LOAD FAQ ---------- */
function loadFAQAnswer() {
  var container = document.getElementById('dashFaqList');
  if (!container) return;
  container.innerHTML = '';
  DASH_FAQ_DATA.forEach(function(item) {
    var el = document.createElement('div');
    el.className = 'dash-faq-item';

    var qEl = document.createElement('div');
    qEl.className = 'dash-faq-q';
    qEl.textContent = DASH_LANG === 'tl' ? item.q_tl : item.q_en;

    var aEl = document.createElement('div');
    aEl.className = 'dash-faq-a';
    aEl.textContent = DASH_LANG === 'tl' ? item.a_tl : item.a_en;

    el.appendChild(qEl);
    el.appendChild(aEl);

    el.addEventListener('click', function() {
      var wasActive = el.classList.contains('active');
      container.querySelectorAll('.dash-faq-item.active').forEach(function(other) {
        other.classList.remove('active');
      });
      if (!wasActive) {
        el.classList.add('active');
      }
    });

    container.appendChild(el);
  });
}

/* ---------- LANGUAGE TOGGLE ---------- */
function toggleLanguage(lang) {
  DASH_LANG = lang;
  document.querySelectorAll('.dash-lang-opt').forEach(function(el) {
    el.classList.toggle('active', el.getAttribute('data-lang') === lang);
  });
  loadFAQAnswer();
}

/* ---------- CHATBOT RESPONSE ---------- */
function getVAWCResponse(question, lang) {
  var msg = question.toLowerCase().trim();
  if (!msg) return lang === 'tl' ? 'Paano kita matutulungan?' : 'How can I help you?';

  var KB = [
    {
      keywords: ['report', 'reporting', 'file', 'submit', 'how to report', 'magreport', 'sumbong', 'isumbong', 'ireport'],
      en: 'To report VAWC, go to your barangay hall and speak with the VAWC Desk officer, visit the nearest PNP WCPD, or contact DSWD. You may also file a report online. All reports are kept confidential.',
      tl: 'Para mag-report ng VAWC, pumunta sa inyong barangay hall at makipag-usap sa VAWC Desk officer, pumunta sa PNP WCPD, o tumawag sa DSWD. Pwede ka ring mag-report online. Lahat ng report ay confidential.'
    },
    {
      keywords: ['abuse', 'abusive', 'abused', 'hurt', 'hit', 'beat', 'abuso', 'inaabuso', 'sinasaktan', 'saktan'],
      en: 'Abuse is never your fault. Whether physical, emotional, sexual, or economic — you deserve to be safe. Report VAWC cases to your barangay, PNP WCPD, or DSWD. Help is available, and you have legal rights to protection.',
      tl: 'Hindi mo kasalanan ang pang-aabuso. Kahit ito ay physical, emotional, sexual, o economic abuse — nararapat kang maging ligtas. I-report ang VAWC sa iyong barangay, PNP WCPD, o DSWD. Nariyan ang tulong, at may karapatan kang maprotektahan.'
    },
    {
      keywords: ['violence', 'violent', 'karahasan', 'marahas'],
      en: 'Violence in any form is not acceptable. Under RA 9262, physical, sexual, psychological, and economic violence against women and children are punishable by law. Reach out to your barangay or call 911 in emergencies.',
      tl: 'Ang karahasan sa anumang anyo ay hindi katanggap-tanggap. Sa ilalim ng RA 9262, ang physical, sexual, psychological, at economic violence laban sa kababaihan at bata ay may parusa sa batas. Makipag-ugnayan sa iyong barangay o tumawag sa 911 kung emergency.'
    },
    {
      keywords: ['legal', 'rights', 'law', 'lawyer', 'attorney', 'court', 'case', 'karapatan', 'abogado', 'pao'],
      en: 'Victims have rights: protection orders (BPO/TPO/PPO), free legal assistance from PAO, confidentiality, and the right to pursue legal action. You do not need a lawyer to start — barangay officials can assist you.',
      tl: 'Ang mga biktima ay may karapatan: protection orders (BPO/TPO/PPO), libreng legal na tulong mula sa PAO, confidentiality, at karapatang magsampa ng kaso. Hindi mo kailangan ng abogado para magsimula — tutulungan ka ng barangay.'
    },
    {
      keywords: ['protection', 'protection order', 'bpo', 'tpo', 'ppo', 'safe', 'safety', 'proteksyon'],
      en: 'Protection orders prohibit the abuser from harming or approaching you. Barangay Protection Orders (BPO) take effect immediately. Temporary (TPO) and Permanent (PPO) orders are issued by the court.',
      tl: 'Ang protection order ay nagbabawal sa nang-aabuso na saktan o lapitan ka. Ang Barangay Protection Order (BPO) ay agad na may bisa. Ang Temporary (TPO) at Permanent (PPO) ay ibinibigay ng korte.'
    },
    {
      keywords: ['barangay', 'kagawad', 'kapitan', 'barangay hall'],
      en: 'Your barangay is your first step. Visit the Barangay VAWC Desk and ask for a Barangay Protection Order (BPO) if you are in danger. They can also refer you to DSWD, PNP, and other agencies.',
      tl: 'Ang iyong barangay ang unang hakbang. Pumunta sa Barangay VAWC Desk at humingi ng Barangay Protection Order (BPO) kung ikaw ay nasa panganib. Maaari ka rin nilang i-refer sa DSWD, PNP, at iba pang ahensya.'
    },
    {
      keywords: ['emergency', 'urgent', 'danger', '911', 'immediate', 'help now', 'saklolo', 'delikado'],
      en: 'If you are in immediate danger, call 911 or go to your nearest barangay hall or police station right away. Contact PNP WCPD at 0919-777-7377 for 24/7 assistance.',
      tl: 'Kung nasa agarang panganib, tumawag sa 911 o pumunta agad sa pinakamalapit na barangay hall o police station. Tawagan ang PNP WCPD sa 0919-777-7377 para sa 24/7 na tulong.'
    },
    {
      keywords: ['confidential', 'confidentiality', 'private', 'anonymous', 'lihim', 'seguridad'],
      en: 'Your report and identity are confidential under Philippine law. Barangay officials, police, and social workers are legally required to keep your information private.',
      tl: 'Ang iyong report at pagkakakilanlan ay confidential sa ilalim ng batas. Ang mga opisyal ng barangay, pulis, at social worker ay legal na kinakailangang panatilihing pribado ang iyong impormasyon.'
    },
    {
      keywords: ['shelter', 'tirahan', 'safe house', 'ligtas', 'masisilungan'],
      en: 'If you need a safe place to stay, DSWD provides temporary shelter and psychosocial support. Your barangay can help coordinate transportation and referral.',
      tl: 'Kung kailangan mo ng ligtas na matutuluyan, ang DSWD ay nagbibigay ng temporary shelter at psychosocial support. Ang iyong barangay ay makakatulong sa transportasyon at referral.'
    },
    {
      keywords: ['support', 'tulong', 'help', 'aid', 'emotional'],
      en: 'You are not alone. Reach out to DSWD for psychosocial support, talk to a trusted friend or family member, or contact a local women\'s organization. You deserve to be heard.',
      tl: 'Hindi ka nag-iisa. Makipag-ugnayan sa DSWD para sa psychosocial support, makipag-usap sa pinagkakatiwalaang kaibigan o kapamilya. Karapat-dapat kang pakinggan.'
    },
    {
      keywords: ['children', 'child', 'minor', 'bata', 'anak', 'menor'],
      en: 'Children have special protection under RA 9262 and RA 7610. Minors can report abuse with or without a guardian. DSWD provides immediate intervention and care.',
      tl: 'Ang mga bata ay may espesyal na proteksyon sa ilalim ng RA 9262 at RA 7610. Pwedeng mag-report ang mga menor de edad kahit walang kasamang magulang. Ang DSWD ay nagbibigay ng agarang tulong.'
    },
    {
      keywords: ['financial', 'economic', 'money', 'support', 'sustento', 'pera', 'pinansyal'],
      en: 'Economic abuse — withholding financial support, controlling money, or preventing you from working — is recognized under RA 9262. The court can order support payments.',
      tl: 'Ang economic abuse — pagpigil ng sustento, pagkontrol ng pera, o pagbawal sa iyo na magtrabaho — ay kinikilala sa ilalim ng RA 9262. Ang korte ay maaaring mag-utos ng sustento.'
    },
    {
      keywords: ['emotional abuse', 'psychological', 'verbal', 'gaslighting', 'damdamin'],
      en: 'Emotional and psychological abuse is real and punishable under RA 9262. This includes threats, intimidation, humiliation, and controlling behavior. You have the right to report it.',
      tl: 'Ang emotional at psychological abuse ay totoo at may parusa sa ilalim ng RA 9262. Kasama rito ang pananakot, pagpapahiya, at pagkontrol. May karapatan kang mag-report.'
    },
    {
      keywords: ['physical abuse', 'physical', 'hitting', 'pananakit', 'suntok', 'sipa'],
      en: 'Physical abuse is serious. Seek medical attention immediately at any government hospital (free treatment). Report the incident to your barangay or the police.',
      tl: 'Malubha ang physical abuse. Agad na humingi ng medical attention sa anumang government hospital (libreng gamutan). I-report ang insidente sa barangay o pulis.'
    },
    {
      keywords: ['harassment', 'stalking', 'bastos', 'catcalling', 'bastosin'],
      en: 'Harassment and stalking are prohibited under RA 11313 (Safe Spaces Act) and RA 9262. Report to your barangay or PNP WCPD.',
      tl: 'Ang harassment at stalking ay ipinagbabawal sa ilalim ng RA 11313 (Safe Spaces Act) at RA 9262. I-report sa barangay o PNP WCPD.'
    },
    {
      keywords: ['threat', 'threats', 'pananakot', 'binantaan', 'pinagbabantaan'],
      en: 'Threats are a serious form of abuse under RA 9262. Report to your barangay and request a Barangay Protection Order (BPO) immediately.',
      tl: 'Ang pananakot ay malubhang uri ng pang-aabuso. I-report sa barangay at humingi agad ng Barangay Protection Order (BPO).'
    },
    {
      keywords: ['control', 'controlling', 'kinokontrol', 'pagkontrol', 'manipulate'],
      en: 'Controlling behavior is a form of psychological abuse. This includes restricting freedom, isolating you from others, and making all decisions for you. You have the right to your own freedom.',
      tl: 'Ang pagkontrol ay isang uri ng psychological abuse. Kasama rito ang pagpigil ng kalayaan at paghihiwalay sa iyo sa iba. May karapatan ka sa iyong sariling kalayaan.'
    },
    {
      keywords: ['ano', 'paano', 'gawin', 'gagawin', 'what to do', 'saan', 'ano ang'],
      en: 'Steps you can take: 1) If in danger, call 911. 2) Visit your Barangay VAWC Desk. 3) File a BPO. 4) Contact DSWD or PNP WCPD. 5) Do not blame yourself — you deserve support.',
      tl: 'Mga hakbang: 1) Kung nasa panganib, tumawag sa 911. 2) Pumunta sa Barangay VAWC Desk. 3) Humingi ng BPO. 4) Tawagan ang DSWD o PNP WCPD. 5) Huwag sisihin ang sarili — karapat-dapat kang tumanggap ng suporta.'
    }
  ];

  var bestScore = 0;
  var bestResponse = null;

  for (var i = 0; i < KB.length; i++) {
    var entry = KB[i];
    for (var j = 0; j < entry.keywords.length; j++) {
      var kw = entry.keywords[j];
      if (msg.indexOf(kw) !== -1) {
        if (kw.length > bestScore) {
          bestScore = kw.length;
          bestResponse = lang === 'tl' ? entry.tl : entry.en;
        }
      }
    }
  }

  if (bestResponse) return bestResponse;

  return lang === 'tl'
    ? 'Paumanhin, ngunit ang VAWC Assistant ay makakatulong lamang sa mga tanong tungkol sa VAWC, pang-aabuso, pag-report, legal na karapatan, proteksyon, at suporta para sa biktima. Paano kita matutulungan?'
    : 'I can only assist with VAWC-related concerns. Please ask about reporting abuse, legal rights, protection orders, safety, or support services. How can I help you?';
}

/* ---------- SEND CHAT MESSAGE ---------- */
function sendVAWCMessage() {
  var input = document.getElementById('dashChatInput');
  var container = document.getElementById('dashChatMessages');
  if (!input || !container) return;

  var text = input.value.trim();
  if (!text) return;

  input.value = '';

  var userMsg = document.createElement('div');
  userMsg.className = 'dash-msg dash-msg-user';
  userMsg.innerHTML = '<div class="dash-msg-text">' + escapeHtml(text) + '</div>';
  container.appendChild(userMsg);
  container.scrollTop = container.scrollHeight;

  setTimeout(function() {
    var reply = getVAWCResponse(text, DASH_LANG);
    var botMsg = document.createElement('div');
    botMsg.className = 'dash-msg dash-msg-bot';
    botMsg.innerHTML = '<div class="dash-msg-text">' + escapeHtml(reply) + '</div>';
    container.appendChild(botMsg);
    container.scrollTop = container.scrollHeight;
  }, 600 + Math.random() * 600);
}

/* ---------- HELPER ---------- */
function escapeHtml(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}
