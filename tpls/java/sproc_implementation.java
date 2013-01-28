{{ package }}import org.springframework.stereotype.Repository;
import de.zalando.sprocwrapper.AbstractSProcService;
import de.zalando.sprocwrapper.dsprovider.{{ datasourceProvider }};
{{ importList }}
@Repository
public class {{ interfaceName }}Impl
    extends AbstractSProcService<{{ interfaceName }}, {{ datasourceProvider }}>
    implements {{ interfaceName }} {

    @Autowired
    public {{ interfaceName }}Impl(final {{ datasourceProvider }} ps) {
        super(ps, {{ interfaceName }}.class);
    }

{{ functionImplementations }}
}
