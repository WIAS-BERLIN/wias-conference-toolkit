###########################
# Manual Name Corrections #
###########################

manual_corrections = {
    "yidiat Omolade": "Yidiat Omolade", #unilorin.edu.ng/index....
    "Hosseini nejad": "Hosseini Nejad", #usually Nejad seems to be capitalized on wikipedia
    "Den Hertog": "den Hertog",
    "De Klerk": "de Klerk",
    "Bot": "Boţ",
    "Hoemberg": "Hömberg",
    "Brueggemann": "Brüggemann",
    "Kroener": "Kröner",
}


#########################
# Math in the abstracts #
#########################

LaTeXShorts = (("MATH", r"\ensuremath"),
               ("NMCAL", r""), #normal upper O
               ("MCAL{l}", r"\ell"), #normal upper O
               #("MCAL", r"\mathcal"),
               ("OPNAME", r"\operatorname"),
)

#TODO: Do we change eps to \epsilon?
math_replacements = (
("O(1/ε)", r"MATH{MCAL{O}(1/\epsilon)}"),
("p × n-dimensional", r"MATH{p \times n}-dimensional"),
("p points", "MATH{p} points"),
("p solutions", "MATH{p} solutions"),
("Denoting n", "Denoting MATH{n}"),
("O(( m+n)log(1/eps) + 1/eps^3)", r"MATH{NMCAL{O}(( m+n)\log(1/OPNAME{eps}) + 1/OPNAME{eps}^3)}"),
("O(m+n+(m+n)^{2/3}/eps^2)", "MATH{NMCAL{O}(m+n+(m+n)^{2/3}/OPNAME{eps}^2)}"),
#("m+n+(m+n)^{2/3}/eps^2", "m+n+(m+n)$^{2/3}$/OPNAME{eps}$^2$"      ),
#("1/eps^3",        "1/OPNAME{eps}$^3$"                           ),
("O(1/T)", r"MATH{NMCAL{O}(1/T)}"),
("O(log(T)/sqrt(T))", "MATH{NMCAL{O}(OPNAME{log}(T)/OPNAME{sqrt}(T))}"),
("0 < p < = 1",    r"MATH{0 < p\leq 1}"                   ), #26389
("k-sparse",       "MATH{k}-sparse"                      ),
("k-Sparse",       "MATH{k}-Sparse"                      ),
("l0-norm",        "MATH{MCAL{l}_0}-norm"                       ),
("l1-norm",        "MATH{MCAL{l}_1}-norm"                       ),
("l1-TV",          "MATH{MCAL{l}_1}-TV"                         ),
("l2-norm",        "MATH{MCAL{l}_2}-norm"                       ),
("m > poly(k)",    "MATH{m>OPNAME{poly}(k)}"      ),
("$O(1/k^(3d+1)/2)$",     "MATH{O(1/k^{(3d+1)/2})}"          ),
("Let D be",              "Let MATH{D} be"                  ),
("(1-epsilon) D and D",   r"MATH{(1-OPNAME{epsilon}) D} and MATH{D}"),
("(1-ϵ) D and D",   r"MATH{(1-\epsilon) D} and MATH{D}"),
("exp(c sqrt(n))", r"MATH{\exp(c OPNAME{sqrt}(n))}"),
("c>0",            "MATH{c>0}"                           ),
("polytope P",     "polytope MATH{P}"                    ),
("$1-\O{1/r}$",    "MATH{1-NMCAL{O}(1/r)}"            ),
('"',   "''"                                             ), #this unifies the quotation marks, tehn they are corrected  by string = replace_all(string, corr.quotation_replacements)
("&",   r"\&"                                             ),
("%",   r"\%"                                             ),
("∈",   r"MATH{\in}"                                      ),
("×",   r"MATH{\times}"                                   ),
("α>0", r"MATH{\alpha>0}"                                 ),
("α",   r"MATH{\alpha}"                                   ),
('θ < k^{3/4}',    "MATH{θ < k^{3/4}}"                   ),
("θ",              r"MATH{\theta}"                        ),
('H_infinity',     r"MATH{H_\infty}"                      ),
('H_{∞}',          r"MATH{H_\infty}"                      ),
('L^oo',           r"MATH{L^\infty}"                      ),
("L-infinity trust region", r"MATH{L^\infty} trust region" ),
('L^2',            "MATH{L^2}"                           ),
('H^1',            "MATH{H^1}"                           ),
('Y^*',            "MATH{Y^*}"                           ),
("O(1/ε^2)",       r"MATH{O(1/\epsilon^2)}"               ),
("1 - ε",              r"MATH{1-\epsilon}"                      ),
("ε",              r"MATH{\epsilon}"                      ),
("ϵ",              r"MATH{\epsilon}"                      ),
("κ",              r"MATH{\kappa}"                        ),
("O(1/r^2)",       "MATH{NMCAL{O}(1/r^2)}"            ),
("O((log r)/r)",   r"MATH{NMCAL{O}(\log r/r)}"         ),
("O(((log r)/r)^2)",      r"MATH{NMCAL{O}((\log r/r)^2)}"),
('TGV^2',          "TGV$^2$"                             ),
(' 1/r^2',         " MATH{1/r^2}"                         ),
('T_{min}',        r"MATH{T_{\min}}"                      ),
('O(d^2/l^2)',     "MATH{NMCAL{O}(d^2/l^2)}"                    ),
#(' \Omega(',       r" MATH{\Omega}("                      ),
(r"\Omega(log n/log log n)", r"MATH{\Omega(\log n/\log \log n)}"), 
(r" \cite{burer2003nonlinear}", ""                        ),
('\u200e',                      ""                        ),
('\u200f',                      ""                        ),
("K-scalable",       "MATH{K}-scalable"       ),
("K-means",          "MATH{K}-means"          ),
("(K being",         "(MATH{K} being"         ),
("as K increases",   "as MATH{K} increases"   ),
("K-indicators",     "MATH{K}-indicators"     ),
("of m+1", "of MATH{m+1}"),
("the L0 ''norm''", "the MATH{L^0} ''norm''"), #TODO: l0?
("simplex-constrained L0 proximal", "simplex-constrained MATH{L^0} proximal"), #TODO: l0?
("p is much smaller than n", "MATH{p} is much smaller than MATH{n}"),
("n x p matrices", r"MATH{n \times p} matrices"),
("p-dimensional", "MATH{p}-dimensional"),
("p-factor", "MATH{p}-factor"),
("Lasso (L1)", "Lasso (MATH{L^1})"), #TODO: l1?
("0th", "MATH{0}th"),
("variable X", "variable MATH{X}"),
("low-rank X", "low-rank MATH{X}"),
("l1-regularized", "MATH{MCAL{l}_1}-regularized"),
("functions f(x)", "functions MATH{f(x)}"),
("of f(x)", "of MATH{f(x)}"),
("L0-norm", "MATH{L^0}-norm"),
("l0-min", "MATH{l^0}-min"),
("L1 norm", "MATH{L^1} norm"),
("L2 norm", "MATH{L^2} norm"),
("L2-loss", "MATH{L^2}-loss"),
("lp-regularized", "MATH{MCAL{l}_p}-regularized"),
("order (n+1)", "order MATH{(n+1)}"),
("when s>1/2", "when MATH{s>1/2}"),
("interval (-1,1)", "interval MATH{(-1,1)}"),
("(1,1) block", "MATH{(1,1)} block"),
("NP -Hard", "NP-hard"), #TODO: fix in converia
("q-th order", "MATH{q}-th order"),
("j(u)=f(u)+g(u).", "MATH{j(u)=f(u)+g(u)}."),
("in P where P is", "in MATH{P} where MATH{P} is"),
("in P when P", "in MATH{P} when MATH{P}"),
("P is empty", "MATH{P} is empty"),
("depends on max(m,n)", "depends on MATH{max(m,n)}"),
("set B.", "set MATH{B}."),
("set B,", "set MATH{B},"),
("of B.", "of MATH{B}."),
("Let (X,d)", "Let MATH{(X,d)}"),
("cover X.", "cover MATH{X}."),
("at most 2r", "at most MATH{2r}"),
(" r ", " MATH{r} "),
(" k ", " MATH{k} "),
(" k.", " MATH{k}."),
(" K ", " MATH{K} "),
(" K.", " MATH{K}."),
(" f ", " MATH{f} "),
(" f.", " MATH{f}."),
(" D ", " MATH{D} "),
(" n ", " MATH{n} "),
(" 2r ", " MATH{2r} "),
(" r>2 ", " MATH{r>2} "),
(" O(1)", " MATH{NMCAL{O}(1)}"),
(" O(n) ", " MATH{NMCAL{O}(n)} "),
(" O(1/t)", " MATH{NMCAL{O}(1/t)}"),
(" O(1/k) ", " MATH{NMCAL{O}(1/k)} "),
(" O(log 1/epsilon) ", r" MATH{NMCAL{O}(\log 1/OPNAME{epsilon})} "),
(" O(1/epsilon)", r" MATH{NMCAL{O}(1/OPNAME{epsilon})}"),
("forward--backward", "forward-backward"),
("forward—backward", "forward-backward"),
(" L1 ", " MATH{L^1} "),
(" L1-", " MATH{L^1}-"),
("method--SEGA", "method --SEGA"),
)
#string = string.replace('\n\n','\n').replace('"',"''")

#####################
# Institution Names #
#####################

#correctly written institutions
exceptions = [
        "RIKEN AIP", #https://aip.riken.jp/
]

#full-string replacement dictionary
full_replacement_dict = {
        "ETH Zurich": "ETH Zürich",
        "UNIVERSITY OF CAMBRIDGE": "University of Cambridge",
        "UNIVERSITY OF IOWA": "University of Iowa",
        "Behbahan khatam Alanbia university of technology": "Behbahan Khatam Alanbia University of Technology",
        "KU Leuven ­- University of Leuven": "KU Leuven",
        "King Abdullah University of Science KAUST": "King Abdullah University of Science (KAUST)",
        "King Abdullah University of science and technology":
        "King Abdullah University of Science and Technology",
        "University of Wisconsin": "University of Wisconsin-Madison",
        "Wisconsin Institute for Discovery": "University of Wisconsin-Madison",
        "Dr.-Ing. h.c. Porsche AG": "Porsche AG",
        "Inria and Ecole Polytechnique": "Inria / Ecole Polytechnique",
}
#Inra -> INRA?

#substrings that need to be removed
delete_parts = [ #only applies from correction_level 2. We probably don't do that
        " Faculty of Mathematics and Information Science, Systems Research Institute,",
        "Department of Applied Mathematics and Statistics, ",
        "Institute of Applied Mathematics, Academy of Mathematics and Systems Science, ",
        ", Nigeria",
        " (Austria)",
        ", Schweiz",
        ", the Netherlands",
        ", Italy",
        " - Italy",
        ", USA",
        ]

#corrections of substrings
partial_replacement_dict = {
        "Zurich": "Zürich",
        "Zuerich": "Zürich",
        "uenchen": "ünchen",
        "versitaet": "versität",
        "Friedrich-Alexander Universität": "Friedrich-Alexander-Universität",
        "Otto-von-Guericke Universität": "Otto-von-Guericke-Universität",
        "Hong KOng": "Hong Kong",
        "nivversi": "niversi",
        "Uni ":"Universität ",
        "Institut polytechnique": "Institut Polytechnique",
        "universit": "Universit",
        "Univerity": "University",
        "Univerisity": "University",
        "Insead": "INSEAD",
        "CNRS & Ecole": "CNRS / École",
        "CNRS and Ecole": "CNRS / École",
}
#Insead -> INSEAD? (acc. to german wiki Insead is legit)
#Chemnitz University of Technology -> TU Chemnitz?

#auffaellige Namen
a_n = """
WIAS
Warsaw University of ...long
Technical University of Munic
TU Muenchen
Department of Applied Mathematics and Statistics, State University of New York-Korea
Academy of Mathematics and System Science, Chinese Academy of Science
LIGM (UMR CNRS 8049)
Institute of Control Sciences
Institute of Applied Mathematics, ...
Faculdade de Engenharia da Universidade de Porto?

"""
