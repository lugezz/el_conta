import datetime

import pandas as pd

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.http.response import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import TemplateView

from export_lsd.models import BasicExportConfig, BulkCreateManager, Empleado, Empresa, Liquidacion, Presentacion
from export_lsd.forms import ConfigEBForm, EmpresaForm, EmpleadoForm, LiquidacionForm, PeriodoForm
from export_lsd.tools.export_advanced_txt import (get_final_txts, get_summary_txtF931,
                                                  process_liquidacion, update_presentacion_info)
from export_lsd.tools.export_basic_txt import export_txt
from export_lsd.tools.import_empleados import get_employees


EXPORT_TITLES = ['Leg', 'Concepto', 'Cant', 'Monto', 'Tipo']


def error_404(request, exception):
    return render(request, 'export_lsd/404.html')


# ------------- DASHBOARD ------------------------------------------------
class HomeView(TemplateView):
    template_name = 'export_lsd/home.html'

    def get_context_data(self, **kwargs):
        presentaciones = Presentacion.objects.filter(empresa__user=self.request.user, closed=True)
        presentaciones_this_year = presentaciones.filter(created__year=datetime.datetime.today().year).count()
        presentaciones_top5 = presentaciones.order_by('-created')[:5]

        context = super().get_context_data(**kwargs)
        context['presentaciones'] = presentaciones
        context['presentaciones_this_year'] = presentaciones_this_year
        context['presentaciones_top5'] = presentaciones_top5
        context['empresas'] = Empresa.objects.filter(user=self.request.user).count()
        context['empleados'] = Empleado.objects.filter(empresa__user=self.request.user).count()
        context['user'] = self.request.user

        return context


# ------------- EMPRESAS ------------------------------------------------
class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'export_lsd/empresa/list.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Empresa.objects.filter(user=self.request.user):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_queryset(self):
        return Empresa.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Empresas'
        context['create_url'] = reverse_lazy('export_lsd:empresa_create')
        context['list_url'] = reverse_lazy('export_lsd:empresa_list')
        context['entity'] = 'Empresas'
        return context


class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'export_lsd/empresa/create.html'
    success_url = reverse_lazy('export_lsd:empresa_list')
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()  # Es lo mismo que escribir form = EmpresaForm(request.POST)
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Agregar Empresa'
        context['list_url'] = reverse_lazy('export_lsd:empresa_list')
        context['entity'] = 'Empresas'
        context['action'] = 'add'
        return context


class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'export_lsd/empresa/create.html'
    success_url = reverse_lazy('export_lsd:empresa_list')
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()  # Es lo mismo que escribir form = EmpresaForm(request.POST)
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'

        except Exception as e:
            data['error'] = e

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Empresa'
        context['list_url'] = reverse_lazy('export_lsd:empresa_list')
        context['entity'] = 'Empresas'
        context['action'] = 'edit'
        return context


class EmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'export_lsd/empresa/delete.html'
    success_url = reverse_lazy('export_lsd:empresa_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = e

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Empresa'
        context['list_url'] = reverse_lazy('export_lsd:empresa_list')
        context['entity'] = 'Empresas'
        return context


# ------------- EMPLEADOS ------------------------------------------------
class EmpleadoListView(LoginRequiredMixin, ListView):
    model = Empleado
    template_name = 'export_lsd/empleado/list.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Empleado.objects.filter(empresa__user=self.request.user):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_queryset(self):
        return Empleado.objects.filter(empresa__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Empleados'
        context['create_url'] = reverse_lazy('export_lsd:empleado_create')
        context['import_url'] = reverse_lazy('export_lsd:import_empleados')
        context['list_url'] = reverse_lazy('export_lsd:empleado_list')
        context['entity'] = 'Empleados'
        return context


class EmpleadoCreateView(LoginRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'export_lsd/empleado/create.html'
    success_url = reverse_lazy('export_lsd:empleado_list')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        form = super(EmpleadoCreateView, self).get_form()
        form.fields['empresa'].queryset = Empresa.objects.filter(user=self.request.user)
        return form

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de un Empleado'
        context['entity'] = 'Empleados'
        context['list_url'] = reverse_lazy('export_lsd:empleado_list')
        context['action'] = 'add'
        return context


class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'export_lsd/empleado/create.html'
    success_url = reverse_lazy('export_lsd:empleado_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de un Empleado'
        context['entity'] = 'Empleados'
        context['list_url'] = reverse_lazy('export_lsd:empleado_list')
        context['action'] = 'edit'
        return context


class EmpleadoDeleteView(LoginRequiredMixin, DeleteView):
    model = Empleado
    template_name = 'export_lsd/empleado/delete.html'
    success_url = reverse_lazy('export_lsd:empleado_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de un Empleado'
        context['entity'] = 'Empleados'
        context['list_url'] = reverse_lazy('export_lsd:empleado_list')
        return context


# ------------- EXPORT ------------------------------------------------
@login_required
def basic_export(request):
    # Debe tener al menos una configuración básica
    basic_export_config_qs = BasicExportConfig.objects.filter(user=request.user)

    if not basic_export_config_qs:
        messages.error(request, "Debe crear al menos un modelo de configuración de Exportación Básica")
        return redirect(reverse_lazy('export_lsd:config_eb_list'))

    # Debe tener al menos una empresa asociada
    empresa_config_qs = Empresa.objects.filter(user=request.user).order_by('name')

    if not empresa_config_qs:
        messages.error(request, "Debe tener al menos asociada una empresa para ")
        return redirect(reverse_lazy('export_lsd:empresa_list'))

    basic_export_config_json = []
    empresa_config_json = []

    for item in basic_export_config_qs:
        basic_export_config_json.append(item.toJSON())

    for item2 in empresa_config_qs:
        empresa_config_json.append(item2.toJSON())

    context = {
        'basic_export_config': basic_export_config_json,
        'empresa_config': empresa_config_json,
        'error': ''
    }

    if request.method == 'POST':
        try:
            txt_original = request.FILES['txtfile']
            cuit = request.POST.get('selectEmpresa')
            fecha_pago_str = request.POST.get('payDay')
            fecha_pago = datetime.datetime.strptime(fecha_pago_str, '%d/%m/%Y')
            export_config = eval(request.POST.get('selectBasicConfig'))

        except ValueError:
            context['error'] = "Formato de archivo incorrecto"
        except Exception as err:
            context['error'] = type(err)

        # Exportación exitosa
        messages.success(request, "Generación de archivo de exportación básica realizada correctamente, \
            archivo disponible para la descarga")

        # 1) Grabo el txt temporalmente
        fs = FileSystemStorage()
        now_str = datetime.datetime.now().strftime('%Y%m%d%H%M')
        fname = f'{request.user.username}_{now_str}.txt'
        file_temp_path = fs.save(f'export_lsd/static/temp/{fname}', txt_original)

        # 2) Proceso el archivo enviando el path como argumento
        txt_final_export_filepath = export_txt(file_temp_path, cuit, fecha_pago, export_config)

        # 3) Elimino el archivo temporal
        fs.delete(file_temp_path)

        # 4) Agrego el path del txt generado al context
        txt_final_export_filepath_static = txt_final_export_filepath.split('/')
        txt_final_export_filepath_static = '/'.join(txt_final_export_filepath_static[-2:])
        context['txt_export_filepath'] = txt_final_export_filepath_static

    return render(request, 'export_lsd/export/basic.html', context)


@login_required
def import_empleados(request):
    result = {
        'error': '',
        'results': '',
        'invalid_data': '',
    }

    if request.method == 'POST':
        # Confirmation button
        if request.POST.get('has_confirmation') == 'Yes':
            data = request.session['all_data']
            bulk_mgr = BulkCreateManager()
            for item in data:
                empresa = Empresa.objects.get(cuit=item[0], user=request.user)
                bulk_mgr.add(Empleado(empresa=empresa, leg=item[1], name=item[2], cuil=item[3], area=item[4]))
            bulk_mgr.done()

            return redirect(reverse_lazy('export_lsd:empleado_list'))
        else:
            try:
                result = get_employees(request.FILES['xlsfile'], request.user)
            except ValueError:
                result['error'] = "Formato de archivo incorrecto"
            except Exception as err:
                result['error'] = type(err)

            request.session['all_data'] = result['results']

    return render(request, 'export_lsd/export/empleados.html', result)


@login_required
def advanced_export(request):
    # Debe tener al menos una empresa asociada
    empresas_qs = Empresa.objects.filter(user=request.user).order_by('name')

    if not empresas_qs:
        messages.error(request, "Debe tener al menos asociada una empresa")
        return redirect(reverse_lazy('export_lsd:empresa_list'))

    presentaciones_en_pr = Presentacion.objects.filter(user=request.user, closed=False).order_by('-periodo')
    form = PeriodoForm(request.POST or None)
    form.fields['empresa'].queryset = Empresa.objects.filter(user=request.user)

    context = {
        'error': '',
        'form': form,
        'presentaciones_en_pr': presentaciones_en_pr,
        'existe_presentacion': 0
    }

    if request.method == 'POST':
        id_empresa = request.POST.get("empresa")
        empresa = Empresa.objects.get(id=id_empresa)
        cuit = empresa.cuit
        periodo = request.POST.get("periodo")
        presentacion = Presentacion.objects.filter(user=request.user,
                                                   empresa__id=id_empresa,
                                                   periodo=f'{periodo}-01')

        per_liq = periodo.replace('-', '')

        # Txt F931 subido
        if 'txtF931' in request.FILES:
            # 1) Grabo el txt temporalmente
            fs = FileSystemStorage()
            fname = f'temptxt_{request.user.username}_{cuit}_{per_liq}.txt'
            fpath = f'export_lsd/static/temp/{fname}'
            fs.delete(fpath)
            fs.save(fpath, request.FILES['txtF931'])

            if presentacion:
                context['existe_presentacion'] = 1

            try:
                context['F931_result'] = get_summary_txtF931(fpath)
            except Exception:
                form = PeriodoForm()
                context['error'] = "Error en el formato del archivo seleccionado"

        # Procesar nomás
        else:
            if presentacion:
                presentacion.delete()

            this_presentacion = Presentacion.objects.create(user=request.user,
                                                            empresa=empresa,
                                                            periodo=f'{periodo}-01')

            return redirect(reverse('export_lsd:advanced_liqs',  kwargs={'pk': this_presentacion.id}))

    return render(request, 'export_lsd/export/advanced.html', context)


@login_required
def advanced_export_liqs(request, pk: int):
    form = LiquidacionForm(request.POST or None)
    periodo_obj = Presentacion.objects.get(id=pk)
    periodo = periodo_obj.periodo
    empresa = periodo_obj.empresa

    liquidaciones_qs = Liquidacion.objects.filter(presentacion=periodo_obj)
    nro_liqs = list(liquidaciones_qs.values_list('nroLiq', flat=True))
    nro_liqs_open = [x for x in range(1, 26) if x not in nro_liqs]

    context = {
        'id_presentacion': pk,
        'liquidaciones': liquidaciones_qs,
        'periodo': periodo,
        'empresa': empresa.name,
        'empleados': periodo_obj.employees,
        'remunerativos': periodo_obj.remunerativos,
        'no_remunerativos': periodo_obj.no_remunerativos,
        'form': form,
        'nro_liqs_open': nro_liqs_open,
        'error': '',
        'success_url': reverse_lazy('export_lsd:home'),
    }

    if request.method == 'POST':
        if 'get-txts' in request.POST:
            # Clic en descargar archivo
            path_txts = get_final_txts(request.user, pk)

            if 'error' in path_txts:
                messages.error(request, path_txts['error'])
            else:
                messages.success(request, "Proceso exitoso, archivo listo para la descarga")
                context['path_txts'] = path_txts['path']

        else:
            df_liq = pd.read_excel(request.FILES['xlsx_liq'])
            nro_liq = request.POST['nroLiq']
            tipo_liq = request.POST['tipo_liq']
            payday = datetime.datetime.strptime(request.POST['payday'], '%d/%m/%Y')

            # Validación 1 - Titulos
            df_titles = list(df_liq.columns.values)
            if df_titles[:5] != EXPORT_TITLES:
                context['error'] = 'Error en el formato del archivo recibido, por favor chequear.'
                return render(request, 'export_lsd/export/advanced_liqs.html', context)

            # Validación 2 - Legajos
            legajos_qs = Empleado.objects.filter(empresa=empresa)
            legajos_db = set(list(legajos_qs.values_list('leg', flat=True)))

            legajos = set(df_liq['Leg'].tolist())

            legajos_dif = legajos.difference(legajos_db)
            if legajos_dif:
                legajos_dif_str = ', '.join(map(str, legajos_dif))
                messages.error(request, f"Empleados {legajos_dif_str} no observados en {empresa.name}")
                return redirect(reverse_lazy('export_lsd:empleado_list'))

            # Procesar la Liquidación
            result = process_liquidacion(pk, nro_liq, payday, df_liq, tipo_liq)
            context['empleados'] = result.get('empleados', 0)
            context['remunerativos'] = result.get('remunerativos', 0)
            context['no_remunerativos'] = result.get('no_remunerativos', 0)
            context['nro_liqs_open'].remove(int(nro_liq))

    return render(request, 'export_lsd/export/advanced_liqs.html', context)

    # TODO: Agregar el borrado de liquidaciones


class PresentacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Presentacion
    template_name = 'export_lsd/export/delete.html'
    success_url = reverse_lazy('export_lsd:advanced')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Presentación'
        context['entity'] = 'Presentaciones'
        context['list_url'] = reverse_lazy('export_lsd:advanced')
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class LiquidacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Liquidacion
    template_name = 'export_lsd/export/delete.html'

    def get_success_url(self):
        liquidacion = Liquidacion.objects.get(id=self.kwargs['pk'])
        id_presentacion = liquidacion.presentacion.id
        return reverse_lazy('export_lsd:advanced_liqs', kwargs={'pk': id_presentacion})

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Liquidación'
        context['entity'] = 'Liquidaciones'
        context['list_url'] = self.get_success_url()
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            update_presentacion_info(self.object.presentacion.id)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class PresentacionListView(LoginRequiredMixin, ListView):
    model = Presentacion
    template_name = 'export_lsd/export/history.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Presentacion.objects.filter(user=self.request.user, closed=True).order_by('-created')[:50]

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Presentacion.objects.filter(user=self.request.user, closed=True):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Presentaciones'
        context['list_url'] = reverse_lazy('export_lsd:presentacion_list')
        context['entity'] = 'Presentaciones'
        return context


# ------------- CONFIGURACIÓN EXPORTACIÓN BÁSICA ------------------------------------------------
class ConfigEBListView(LoginRequiredMixin, ListView):
    model = BasicExportConfig
    template_name = 'export_lsd/config-eb/list.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return BasicExportConfig.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                # TODO: Filtrar por usuarios en todos lados
                for i in BasicExportConfig.objects.filter(user=self.request.user):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Configuraciones de Exportaciones Básicas'
        context['create_url'] = reverse_lazy('export_lsd:config_eb_create')
        context['list_url'] = reverse_lazy('export_lsd:config_eb_list')
        context['entity'] = 'ConfigEB'
        return context


class ConfigEBCreateView(LoginRequiredMixin, CreateView):
    model = BasicExportConfig
    form_class = ConfigEBForm
    template_name = 'export_lsd/config-eb/create.html'
    success_url = reverse_lazy('export_lsd:config_eb_list')
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Agregar Configuración'
        context['list_url'] = reverse_lazy('export_lsd:config_eb_list')
        context['entity'] = 'ConfigEB'
        context['action'] = 'add'
        return context


class ConfigEBUpdateView(LoginRequiredMixin, UpdateView):
    model = BasicExportConfig
    form_class = ConfigEBForm
    template_name = 'export_lsd/config-eb/create.html'
    success_url = reverse_lazy('export_lsd:config_eb_list')
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'

        except Exception as e:
            data['error'] = e

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Configuración'
        context['list_url'] = reverse_lazy('export_lsd:config_eb_list')
        context['entity'] = 'ConfigEB'
        context['action'] = 'edit'
        return context


class ConfigEBDeleteView(LoginRequiredMixin, DeleteView):
    model = BasicExportConfig
    form_class = ConfigEBForm
    template_name = 'export_lsd/config-eb/delete.html'
    success_url = reverse_lazy('export_lsd:config_eb_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = e

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Configuración'
        context['list_url'] = reverse_lazy('export_lsd:config_eb_list')
        context['entity'] = 'ConfigEB'
        return context
