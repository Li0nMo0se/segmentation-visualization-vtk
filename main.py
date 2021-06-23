import itk
import vtk

def render(main_file, segmented_file):
    """
    :param main_file:  path to the regular volume (.mha format)
    :param segmented_file: path to the segmented file (.mha format)
    """
    # Main volume
    reader_main = vtk.vtkMetaImageReader()
    reader_main.SetFileName(main_file)

    volume_mapper_main = vtk.vtkSmartVolumeMapper()
    volume_mapper_main.SetInputConnection(reader_main.GetOutputPort())

    # Opacity -> map intensity to an opacity
    opacity_transfer_function_main = vtk.vtkPiecewiseFunction()
    opacity_transfer_function_main.AddPoint(20, 0.0)
    opacity_transfer_function_main.AddPoint(255, 0.3)

    volume_property_main = vtk.vtkVolumeProperty()
    volume_property_main.SetScalarOpacity(opacity_transfer_function_main)

    # Volume (same as actor)
    volume_main = vtk.vtkVolume()
    volume_main.SetMapper(volume_mapper_main)
    volume_main.SetProperty(volume_property_main)

    # Volume with segmented data
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(segmented_file)

    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputConnection(reader.GetOutputPort())

    # Opacity -> map intensity to an opacity
    opacity_transfer_function = vtk.vtkPiecewiseFunction()

    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(250, 0.0, 0.0, 0.0)
    color_transfer_function.AddRGBPoint(255.0, 1.0, 0.0, 0.0)  # Segmented pixels will be red

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_transfer_function)
    volume_property.SetScalarOpacity(opacity_transfer_function)

    # Volume (same as actor)
    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)

    # Renderer
    ren = vtk.vtkRenderer()
    ren.AddActor(volume_main)  # Add main volume
    ren.AddActor(volume)  # Add volume with segmentation

    ren.SetBackground(0.0, 0.0, 0.0)
    ren.SetBackground2(0.0, 1.0, 1.0)
    ren.SetGradientBackground(1)

    # Window renderer
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    # Window renderer interactor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Start everything
    iren.Initialize()
    renWin.Render()
    iren.Start()


def segment(filename):
    """
    Segmente the two kidneys
    :param filename: path of the input file (.mha format)
    :return: the two segmented kidney
    """
    reader = itk.imread(filename)
    InputImageType = itk.Image[itk.SS, 3]

    seg_filter = itk.ConnectedThresholdImageFilter[InputImageType, InputImageType].New(reader)
    seg_filter.SetUpper(400)
    seg_filter.SetLower(180)
    seg_filter.AddSeed([131, 246, 26])
    seg_filter.AddSeed([411, 317, 69])
    seg_filter.Update()

    OutputImageType = itk.Image[itk.UC, 3]
    rescale_filter = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType].New(seg_filter.GetOutput())
    rescale_filter.Update()

    return rescale_filter

if __name__ == "__main__":
    print(itk.Version.GetITKVersion())

    input_filename = "abdomen.mha"
    segmented_filename = "segmented.mha"

    output = segment(input_filename)
    itk.imwrite(output, segmented_filename)  # Save as uint8

    render(input_filename, segmented_filename)
