library(AnophelesModel)
# entomology parameters
gambiae_ent_params <- def_vector_params(mosquito_species = "Anopheles gambiae")
# host params
default_host_params <- def_host_params()

select_idx = activity_patterns$species == "Anopheles gambiae" &
    activity_patterns$country == "Ghana"
gha_gambiae_biting_pattern <- activity_patterns[select_idx, ]

host_pop = 2000
vec_pop = 10000

model_params <- build_model_obj(
    gambiae_ent_params,
    default_host_params,
    gha_gambiae_biting_pattern,
    host_pop
)

PN2 <- intervention_obj_examples$LLINs_example
PN2$description <- "PN2"
PN2$parameterisation <- "LLINs01"
PN2$LLIN_country <- "Ghana"
PN2$LLIN_type <- "PermaNet 2.0"


PN3 <- intervention_obj_examples$LLINs_example
PN3$description <- "PN3"
PN3$parameterisation <- "LLINs02"
PN2$LLIN_country <- "Ghana"
PN2$LLIN_type <- "PermaNet 3.0"

new_IRS <- intervention_obj_examples$IRS_example
new_IRS$description <- "Permethrin IRS"
new_IRS$parameterisation <- "IRS16"

new_intervention_list <- c(intervention_obj_examples, list(new_IRS = new_IRS))

list_interv <- new_intervention_list
coverages <- c(seq(0, 1, by = 0.1))
n_ip <- 100
intervention_vec <- def_interventions_effects(
    list_interv,
    model_params,
    n_ip,
    verbose = TRUE
)

# vector capacity
impact_gambiae <- calculate_impact_var(
    mosquito_species = "Anopheles gambiae",
    activity_patterns = "default_Anopheles_gambiae",
    interventions = intervention_vec,
    n_sample_points = 10,
    plot_result = FALSE
)
plot_impact_var("Anopheles gambiae", impact_gambiae)

# entomology xml
entomology_xml <- get_OM_ento_snippet(
    gambiae_ent_params,
    default_host_params
)
print(entomology_xml)
# GVI snippets
GVI_snippets <- get_OM_GVI_snippet(
    "Anopheles example",
    impacts$interventions_vec$LLINs_example,
    100,
    plot_f = TRUE
)